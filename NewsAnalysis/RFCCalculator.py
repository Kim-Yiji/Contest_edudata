import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from tqdm import tqdm
import re
import os
import matplotlib.font_manager as fm

# 정책 강도 키워드 사전
POLICY_KEYWORDS = {
    '위기': 1.0,
    '논란': 0.8,
    '전면개편': 0.9,
    '시위': 0.7,
    '법안': 0.6,
    '교육부': 0.5,
    '예산': 0.5,
    '파행': 0.9,
    '충격': 0.8,
    '심각': 0.8,
    '비판': 0.7,
    '우려': 0.6
}

def get_keyword_score(text):
    """키워드 기반 정책 강도 점수 계산"""
    score = 0
    for keyword, weight in POLICY_KEYWORDS.items():
        if keyword in text:
            score += weight
    return min(score, 1.0)  # 최대 1.0으로 제한

def get_sentiment_score(text, tokenizer, model, device):
    """감성분석을 통해 긍정/부정 점수 계산"""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        
    # 긍정(1) 클래스의 확률을 감성 점수로 사용
    sentiment_score = probabilities[0][1].item()
    return sentiment_score

def calculate_criticality_score(news_text, sentiment_score, similarity_score):
    """Criticality 점수 계산 (키워드 + 감성 + 유사도)"""
    # 1. 키워드 기반 점수
    keyword_score = get_keyword_score(news_text)
    
    # 2. 감성 점수 변환 (긍정/부정에 따른 가중치)
    if sentiment_score < 0.3:  # 강한 부정
        sentiment_weight = 1.0
    elif sentiment_score < 0.5:  # 약한 부정
        sentiment_weight = 0.8
    elif sentiment_score > 0.7:  # 강한 긍정
        sentiment_weight = 0.6
    else:  # 중립
        sentiment_weight = 0.4
    
    # 3. 최종 Criticality 점수 계산
    criticality_score = (
        0.4 * keyword_score +  # 키워드 기반 점수
        0.3 * sentiment_weight +  # 감성 가중치
        0.3 * similarity_score  # 유사도 점수
    )
    
    return criticality_score, keyword_score, sentiment_weight

def calculate_frequency_score(category_news, news_df):
    """개선된 Frequency 점수 계산 (출처 다양성 + 지속성 고려)"""
    # 1. 기본 빈도 점수
    total_news = len(news_df)
    news_count = len(category_news)
    base_frequency = news_count / total_news
    
    # 2. 출처 다양성 점수
    unique_sources = category_news['언론사'].nunique()
    total_sources = news_df['언론사'].nunique()
    source_diversity = unique_sources / total_sources
    
    # 3. 지속성 점수 (1년 기준)
    news_dates = pd.to_datetime(category_news['일자'])
    date_range = (news_dates.max() - news_dates.min()).days
    if date_range > 0:
        # 뉴스가 분포된 기간이 길수록 높은 점수 (최대 365일 기준)
        persistence_score = min(date_range / 365, 1.0)
    else:
        persistence_score = 0.1  # 같은 날짜의 뉴스는 낮은 점수
    
    # 4. 최종 Frequency 점수 계산
    frequency_score = (
        0.5 * base_frequency +      # 기본 빈도
        0.3 * source_diversity +    # 출처 다양성
        0.2 * persistence_score     # 지속성
    )
    
    return frequency_score, {
        'base_frequency': base_frequency,
        'source_diversity': source_diversity,
        'persistence_score': persistence_score,
        'date_range_days': date_range  # 날짜 범위도 함께 반환
    }

def calculate_recency_score(news_date, latest_date):
    """연간 정규화된 Recency 점수 계산"""
    # 날짜 차이 계산
    days_diff = (latest_date - news_date).days
    
    # 연간 정규화 (1년 = 365일 기준)
    # 1월 1일 = 0점, 12월 31일 = 1점
    normalized_score = 1 - (days_diff / 365)
    
    # 최소 점수는 0.1로 설정 (과거 뉴스도 일정 가중치 부여)
    return max(normalized_score, 0.1)

def calculate_rfc_scores(classification_df):
    """RFC 점수 계산 및 시각화"""
    print("RFC 점수 계산 중...")
    
    # 날짜 변환
    classification_df['일자'] = pd.to_datetime(classification_df['일자'])
    latest_date = classification_df['일자'].max()
    
    print("감성분석 모델 로딩 중...")
    # 감성분석 모델 및 토크나이저 로드
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-FinBert-SC")
    model = AutoModelForSequenceClassification.from_pretrained("snunlp/KR-FinBert-SC").to(device)
    
    # 대분류별 RFC 점수 계산
    rfc_scores = []
    categories = classification_df['대분류'].unique()
    
    print("\n대분류별 점수 계산 중...")
    for category in tqdm(categories, desc="대분류 처리"):
        category_news = classification_df[classification_df['대분류'] == category]
        
        # Recency 점수 계산 (월간 정규화 방식)
        recency_scores = []
        for _, row in tqdm(category_news.iterrows(), desc=f"{category} Recency 점수 계산", leave=False):
            news_date = pd.to_datetime(row['일자'])
            recency_score = calculate_recency_score(news_date, latest_date)
            recency_scores.append(recency_score)
        avg_recency = np.mean(recency_scores)
        
        # Frequency 점수 계산 (출처 다양성 + 지속성 고려)
        frequency_score, freq_details = calculate_frequency_score(category_news, classification_df)
        
        # Criticality 점수 계산
        criticality_scores = []
        for _, row in tqdm(category_news.iterrows(), desc=f"{category} Criticality 점수 계산", leave=False):
            # 감성 점수 계산
            sentiment_score = get_sentiment_score(row['제목'], tokenizer, model, device)
            # 유사도 점수는 이미 계산되어 있음
            similarity_score = row['유사도']
            # Criticality 점수 계산
            criticality_score, _, _ = calculate_criticality_score(
                row['제목'], 
                sentiment_score, 
                similarity_score
            )
            criticality_scores.append(criticality_score)
        avg_criticality = np.mean(criticality_scores)
        
        # RFC 점수 계산 (가중치: R=0.2, F=0.4, C=0.4)
        rfc_score = (
            0.2 * avg_recency +      # Recency
            0.4 * frequency_score +  # Frequency
            0.4 * avg_criticality    # Criticality
        )
        
        rfc_scores.append({
            '대분류': category,
            'RFC_Score': rfc_score,
            'Recency_Score': avg_recency,
            'Frequency_Score': frequency_score,
            'Criticality_Score': avg_criticality,
            'Frequency_Details': freq_details
        })
    
    print("\n결과 저장 중...")
    # RFC 점수 기준으로 정렬
    rfc_scores = sorted(rfc_scores, key=lambda x: x['RFC_Score'], reverse=True)
    
    # 결과를 DataFrame으로 변환
    rfc_df = pd.DataFrame(rfc_scores)
    
    # 상세 점수 정보를 별도 컬럼으로 분리
    freq_details_df = pd.json_normalize(rfc_df['Frequency_Details'])
    rfc_df = pd.concat([rfc_df.drop('Frequency_Details', axis=1), freq_details_df], axis=1)
    
    # 결과 저장
    rfc_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("그래프 생성 중...")
    # seaborn 그래프 생성
    plt.figure(figsize=(15, 8))
    sns.set_style("whitegrid")
    
    # RFC 점수 기준으로 정렬
    rfc_df = rfc_df.sort_values('RFC_Score', ascending=True)
    
    # 바 그래프 생성
    bars = plt.barh(rfc_df['대분류'], rfc_df['RFC_Score'], color='skyblue')
    
    # 각 막대에 점수 정보 표시
    for i, bar in enumerate(bars):
        width = bar.get_width()
        r_score = rfc_df['Recency_Score'].iloc[i]
        f_score = rfc_df['Frequency_Score'].iloc[i]
        c_score = rfc_df['Criticality_Score'].iloc[i]
        
        # 레이블 텍스트 생성
        label_text = f'RFC: {width:.2f}\nR: {r_score:.2f}\nF: {f_score:.2f}\nC: {c_score:.2f}'
        plt.text(width, i, label_text, 
                 ha='left', va='center', 
                 fontproperties='AppleGothic',
                 fontsize=9)
    
    plt.title('대분류별 RFC 점수 분포', fontsize=14, pad=20, fontproperties='AppleGothic')
    plt.xlabel('RFC 점수', fontsize=12, fontproperties='AppleGothic')
    plt.ylabel('대분류', fontsize=12, fontproperties='AppleGothic')
    
    # y축 레이블의 폰트 설정
    for label in plt.gca().get_yticklabels():
        label.set_fontproperties('AppleGothic')
    
    # 그래프 간격 조정
    plt.tight_layout()
    
    # 그래프 저장
    plt.savefig(plot_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print("완료!")
    
    return rfc_df

if __name__ == "__main__":
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
    input_file = input("RFC 점수를 계산할 파일 경로를 입력하세요 (예: NewsAnalysis/NewsData/Classified/Classified_20250312-20250412.csv): ")

    # 입력 파일 존재 여부 확인
    if not os.path.exists(input_file):
        print(f"오류: 입력 파일이 존재하지 않습니다: {input_file}")
        exit(1)

    # 출력 디렉토리 설정
    rfc_dir = "NewsAnalysis/RFCScore"
    os.makedirs(rfc_dir, exist_ok=True)

    # 입력 파일명에서 날짜 추출
    date_match = re.search(r'\d{8}-\d{8}', input_file)
    if date_match:
        date_str = date_match.group()
        output_file = os.path.join(rfc_dir, f"RFCScore_{date_str}.csv")
        plot_file = os.path.join(rfc_dir, f"RFCScoreGraph_{date_str}.png")
    else:
        # 날짜가 없는 경우 원본 파일명 사용
        base_name = os.path.basename(input_file)
        output_file = os.path.join(rfc_dir, f"RFCScore_{os.path.splitext(base_name)[0]}.csv")
        plot_file = os.path.join(rfc_dir, f"RFCScoreGraph_{os.path.splitext(base_name)[0]}.png")

    print(f"\n입력 파일: {input_file}")
    print(f"출력 파일: {output_file}")
    print(f"통계 그래프: {plot_file}\n")

    # 데이터 로드
    print("데이터 로드 중...")
    classification_df = pd.read_csv(input_file)
    
    # RFC 점수 계산 실행
    print("RFC 점수 계산 중...")
    rfc_scores = calculate_rfc_scores(classification_df)
    
    # 결과 출력
    print("\n=== 대분류별 RFC 점수 ===")
    print(rfc_scores) 