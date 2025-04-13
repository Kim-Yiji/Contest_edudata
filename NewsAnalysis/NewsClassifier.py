import pandas as pd
import json
from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from tqdm import tqdm
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# 폰트 설정
print("\n=== 폰트 설정 확인 ===")
plt.style.use('seaborn-v0_8')

font_path = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'  # 존재하는 폰트 경로 사용
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = font_prop.get_name()
    print(f"폰트 설정: {font_prop.get_name()}")
else:
    print("경고: 한글 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")

plt.rcParams['font.size'] = 12
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['figure.titlesize'] = 14

# 사용자 입력 받기
input_file = input("분류할 파일 경로를 입력하세요 (예: NewsAnalysis/NewsData/Preprocessed/Preprocessed_20250312-20250412.csv): ")

# 입력 파일 존재 여부 확인
if not os.path.exists(input_file):
    print(f"오류: 입력 파일이 존재하지 않습니다: {input_file}")
    exit(1)

# 출력 디렉토리 설정
classified_dir = "NewsAnalysis/NewsData/Classified"
os.makedirs(classified_dir, exist_ok=True)

# 입력 파일명에서 날짜 추출
date_match = re.search(r'\d{8}-\d{8}', input_file)
if date_match:
    date_str = date_match.group()
    output_file = os.path.join(classified_dir, f"Classified_{date_str}.csv")
    plot_file = os.path.join(classified_dir, f"Classified_Graph_{date_str}.png")
else:
    # 날짜가 없는 경우 원본 파일명 사용
    base_name = os.path.basename(input_file)
    output_file = os.path.join(classified_dir, f"Classified_{os.path.splitext(base_name)[0]}.csv")
    plot_file = os.path.join(classified_dir, f"Classified_Graph_{os.path.splitext(base_name)[0]}.png")

print(f"\n입력 파일: {input_file}")
print(f"출력 파일: {output_file}")

# 1. M2 GPU 가속 설정
print("GPU 설정 확인 중...")
if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("Apple M2 GPU 가속 사용 가능")
else:
    device = torch.device("cpu")
    print("GPU 가속 불가능, CPU 사용")

# 2. 모델 로드
print("모델 로딩 중...")
model = SentenceTransformer('jhgan/ko-sroberta-multitask')
model = model.to(device)

# 3. 데이터 로드
print("데이터 로딩 중...")
# 뉴스 데이터 로드
news_df = pd.read_csv(input_file, encoding='utf-8')

# 예산 항목 데이터 로드
budget_keywords_df = pd.read_csv('NewsAnalysis/BaseData/세부항목예시별 LLM기반 키워드확장.csv', encoding='utf-8')

# 중분류와 대분류 정보 매핑 생성 (세부항목예시별 LLM기반 키워드확장.csv에서 직접 사용)
subcategory_to_middle = dict(zip(budget_keywords_df['소분류'], budget_keywords_df['중분류']))
subcategory_to_major = dict(zip(budget_keywords_df['소분류'], budget_keywords_df['대분류']))

# 4. 뉴스 텍스트 전처리
def prepare_news_text(row):
    """뉴스 텍스트 전처리 함수"""
    # 제목은 그대로 유지
    title = row['제목']
    
    # 키워드와 특성추출 결과를 문장처럼 구성
    keywords = row['키워드'].split() if pd.notna(row['키워드']) else []
    features = row['특성추출(가중치순 상위 50개)'].split() if pd.notna(row['특성추출(가중치순 상위 50개)']) else []
    
    # 키워드와 특성추출 결과를 결합하여 의미있는 문장 구성
    keyword_sentence = f"이 기사는 {' '.join(keywords[:10])} 등에 관한 내용을 다룹니다."
    feature_sentence = f"주요 특징은 {' '.join(features[:10])} 등이 있습니다."
    
    return f"{title} {keyword_sentence} {feature_sentence}"

print("뉴스 텍스트 전처리 중...")
news_texts = [prepare_news_text(row) for _, row in tqdm(news_df.iterrows(), total=len(news_df), desc="뉴스 텍스트 전처리")]

# 5. 예산 항목 텍스트 전처리
def prepare_budget_text(row):
    return f"{row['세부항목 예시']} {row['뉴스 일반 표현']}"

print("예산 항목 텍스트 전처리 중...")
budget_texts = [prepare_budget_text(row) for _, row in tqdm(budget_keywords_df.iterrows(), total=len(budget_keywords_df), desc="예산 항목 전처리")]

# 6. 텍스트 임베딩 생성
print("텍스트 임베딩 생성 중...")

# 배치 처리로 임베딩 생성
def get_embeddings(texts, batch_size=32):
    embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="임베딩 생성"):
        batch = texts[i:i + batch_size]
        with torch.no_grad():
            emb = model.encode(batch, convert_to_tensor=True)
            if device.type == "mps":
                emb = emb.to(device)
        embeddings.append(emb)
    return torch.cat(embeddings)

news_embeddings = get_embeddings(news_texts)
budget_embeddings = get_embeddings(budget_texts)

# 7. 유사도 계산 및 매칭
print("유사도 계산 및 매칭 중...")
# MPS에서 cosine_similarity 계산을 위해 CPU로 이동
if device.type == "mps":
    news_embeddings = news_embeddings.cpu()
    budget_embeddings = budget_embeddings.cpu()

similarity_matrix = util.cos_sim(news_embeddings, budget_embeddings)

# 유사도 통계 계산
print("\n=== 유사도 통계 ===")
all_scores = similarity_matrix.flatten().numpy()
print(f"평균 유사도: {np.mean(all_scores):.4f}")
print(f"중앙값 유사도: {np.median(all_scores):.4f}")
print(f"최대 유사도: {np.max(all_scores):.4f}")
print(f"최소 유사도: {np.min(all_scores):.4f}")

# 가장 유사도가 높은 1개 매칭 결과만 추출
results = []
threshold = 0.5  # 임계값

for i in tqdm(range(len(news_df)), desc="매칭 결과 생성"):
    similarities = similarity_matrix[i]
    top_idx = torch.argmax(similarities).item()
    top_score = similarities[top_idx].item()
    
    if top_score >= threshold:
        subcategory = budget_keywords_df.iloc[top_idx]['소분류']
        middle_category = subcategory_to_middle.get(subcategory, 'Unknown')  # 중분류 정보 가져오기
        major_category = subcategory_to_major.get(subcategory, 'Unknown')  # 대분류 정보 가져오기
        
        # 원본 데이터의 모든 열을 포함
        result = {
            '뉴스 식별자': news_df.iloc[i]['뉴스 식별자'],
            '일자': news_df.iloc[i]['일자'],
            '언론사': news_df.iloc[i]['언론사'],
            '제목': news_df.iloc[i]['제목'],
            '키워드': news_df.iloc[i]['키워드'],
            '특성추출(가중치순 상위 50개)': news_df.iloc[i]['특성추출(가중치순 상위 50개)'],
            'URL': news_df.iloc[i]['URL'],
            # 분류 결과 추가
            '대분류': major_category,
            '중분류': middle_category,
            '소분류': subcategory,
            '세부항목 예시': budget_keywords_df.iloc[top_idx]['세부항목 예시'],
            '뉴스 일반 표현': budget_keywords_df.iloc[top_idx]['뉴스 일반 표현'],
            '유사도': float(top_score)
        }
        results.append(result)

# 8. 결과 저장
print("결과 저장 중...")
results_df = pd.DataFrame(results)

# 열 순서 조정
column_order = [
    '뉴스 식별자', '일자', '언론사', '제목', '키워드', 
    '특성추출(가중치순 상위 50개)', 'URL',
    '대분류', '중분류', '소분류', 
    '세부항목 예시', '뉴스 일반 표현', '유사도'
]
results_df = results_df[column_order]

# 유사도 기준으로 정렬
results_df = results_df.sort_values('유사도', ascending=False)

# 결과 저장
results_df.to_csv(output_file, index=False, encoding='utf-8')

# 9. 대분류별 결과 시각화
print("\n대분류별 결과 시각화 중...")

# 대분류별 통계 계산
major_category_stats = results_df.groupby('대분류').agg({
    '뉴스 식별자': 'count',
    '유사도': 'mean'
}).reset_index()
major_category_stats.columns = ['대분류', '기사수', '평균유사도']

# 그래프 생성
plt.figure(figsize=(15, 8))
sns.set_style("whitegrid")

# 기사 수 기준으로 정렬
major_category_stats = major_category_stats.sort_values('기사수', ascending=True)

# 바 그래프 생성
bars = plt.barh(major_category_stats['대분류'], major_category_stats['기사수'], color='skyblue')

# 각 막대에 기사 수와 평균 유사도 표시
for i, bar in enumerate(bars):
    width = bar.get_width()
    avg_similarity = major_category_stats['평균유사도'].iloc[i]
    
    # 레이블 텍스트 생성
    label_text = f'기사수: {width:,}\n평균유사도: {avg_similarity:.3f}'
    plt.text(width, i, label_text, 
             ha='left', va='center', 
             fontproperties='AppleGothic',
             fontsize=9)

plt.title('대분류별 뉴스 기사 분포', fontsize=14, pad=20, fontproperties='AppleGothic')
plt.xlabel('기사 수', fontsize=12, fontproperties='AppleGothic')
plt.ylabel('대분류', fontsize=12, fontproperties='AppleGothic')

# y축 레이블의 폰트 설정
for label in plt.gca().get_yticklabels():
    label.set_fontproperties('AppleGothic')

# 그래프 간격 조정
plt.tight_layout()

# 그래프 저장
date_str = re.search(r'\d{8}-\d{8}', input_file).group() if re.search(r'\d{8}-\d{8}', input_file) else "results"
plot_file = os.path.join(classified_dir, f"Classified_Graph_{date_str}.png")
plt.savefig(plot_file, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print("분류 완료!")
print(f"총 {len(results)} 개의 매칭 결과가 저장되었습니다.")
print(f"결과 파일: {output_file}")
print(f"통계 그래프: {plot_file}")
print("\n=== 상위 10개 매칭 결과 ===")
# 선택된 열만 출력
selected_columns = ['일자', '언론사', '제목', '대분류', '중분류', '소분류', '유사도']
print(results_df[selected_columns].head(10).to_string(index=False)) 