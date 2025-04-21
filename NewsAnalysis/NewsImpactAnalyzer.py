import pandas as pd
import numpy as np
from datetime import datetime
import os
import re
from collections import Counter
import torch
from torch.nn.functional import cosine_similarity
from tqdm import tqdm
import shutil
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

def calculate_keyword_similarity(news_df):
    """키워드 기반 뉴스 간 유사도 계산 (Scikit-learn + GPU 가속)"""
    print("키워드 기반 유사도 계산 중...")
    
    # M2 GPU 설정
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"사용 중인 방식: {'GPU 가속' if device.type == 'mps' else 'CPU'}")
    
    print("\n1. 키워드 벡터화 중...")
    # CountVectorizer를 사용하여 키워드 벡터화
    vectorizer = CountVectorizer(tokenizer=lambda x: x.split(), 
                               lowercase=False,
                               binary=True)  # 키워드 존재 여부만 고려
    
    # 키워드 벡터화 (병렬 처리)
    keyword_matrix = vectorizer.fit_transform(news_df['특성추출(가중치순 상위 50개)'].fillna(''))
    print(f"총 {keyword_matrix.shape[1]}개의 유니크 키워드가 추출되었습니다.")
    
    print("\n2. 코사인 유사도 계산 중...")
    # 배치 처리를 위한 설정
    batch_size = 1000  # 배치 크기 증가 (희소 행렬 사용으로 메모리 효율적)
    num_news = len(news_df)
    
    # 결과를 저장할 임시 파일 생성
    temp_dir = "temp_similarity"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 배치 단위로 코사인 유사도 계산
    for i in tqdm(range(0, num_news, batch_size), total=num_news//batch_size + 1, desc="유사도 계산"):
        batch_end = min(i + batch_size, num_news)
        
        # 현재 배치와 모든 벡터 간의 유사도 계산
        batch_similarities = cosine_similarity(
            keyword_matrix[i:batch_end],
            keyword_matrix
        )
        
        # 배치 결과를 디스크에 저장
        np.save(os.path.join(temp_dir, f"batch_{i}.npy"), batch_similarities)
        
        # 메모리 해제
        del batch_similarities
    
    print("\n3. 결과 병합 중...")
    # 모든 배치 결과를 하나의 행렬로 병합
    similarity_matrix = np.zeros((num_news, num_news))
    for i in tqdm(range(0, num_news, batch_size), desc="결과 병합"):
        batch_end = min(i + batch_size, num_news)
        batch_data = np.load(os.path.join(temp_dir, f"batch_{i}.npy"))
        similarity_matrix[i:batch_end] = batch_data
    
    # 임시 파일 삭제
    shutil.rmtree(temp_dir)
    
    print("\n유사도 계산 완료!")
    return similarity_matrix

def calculate_news_impact_score(news_df, target_news, similarity_matrix, target_idx):
    """
    뉴스의 영향력 점수 계산
    1. C 점수 (기존 criticality_score)
    2. 유사 뉴스의 언론사 다양성
    3. 유사 뉴스의 빈도
    """
    # 1. C 점수 (40%)
    c_score = target_news['criticality_score']
    
    # 2. 유사 뉴스의 언론사 다양성 (30%)
    # 유사도가 0.5 이상인 뉴스들만 고려
    similar_indices = np.where(similarity_matrix[target_idx] >= 0.5)[0]
    similar_news = news_df.iloc[similar_indices]
    media_diversity = similar_news['언론사'].nunique() / news_df['언론사'].nunique()
    
    # 3. 유사 뉴스의 빈도 (30%)
    # 유사 뉴스의 수를 로그 스케일로 정규화
    similar_news_count = len(similar_news)
    # 최대 유사 뉴스 수를 100으로 가정하고 정규화
    max_expected_similar = 100
    frequency_score = min(1.0, np.log1p(similar_news_count) / np.log1p(max_expected_similar))
    
    # 최종 점수 계산
    impact_score = (
        0.4 * c_score +          # C 점수
        0.3 * media_diversity +  # 언론사 다양성
        0.3 * frequency_score    # 유사 뉴스 빈도
    )
    
    return impact_score, {
        'c_score': c_score,
        'media_diversity': media_diversity,
        'frequency_score': frequency_score,
        'similar_news_count': similar_news_count,
        'similar_indices': similar_indices.tolist()
    }

def select_top_news(impact_df, similarity_matrix, similarity_threshold=0.7):
    """유사한 뉴스가 중복되지 않도록 상위 뉴스 선정"""
    selected_indices = []
    remaining_indices = impact_df.index.tolist()
    
    while len(selected_indices) < 10 and remaining_indices:
        # 남은 뉴스 중 가장 높은 영향력 점수를 가진 뉴스 선택
        current_idx = remaining_indices[0]
        selected_indices.append(current_idx)
        
        # 선택된 뉴스와 유사한 뉴스들을 제외
        similar_indices = np.where(similarity_matrix[current_idx] >= similarity_threshold)[0]
        remaining_indices = [idx for idx in remaining_indices if idx not in similar_indices]
    
    return impact_df.loc[selected_indices]

def generate_monthly_report(input_file, output_file):
    """월별 뉴스 영향력 분석 리포트 생성"""
    print("뉴스 영향력 분석 중...")
    
    # 데이터 로드
    df = pd.read_csv(input_file)
    
    # C score 파일 경로 찾기
    date_match = re.search(r'\d{8}-\d{8}', input_file)
    if date_match:
        date_str = date_match.group()
        c_score_file = os.path.join('NewsAnalysis/RFCData/C_score', f"CScore_{date_str}.csv")
    else:
        base_name = os.path.basename(input_file)
        c_score_file = os.path.join('NewsAnalysis/RFCData/C_score', f"CScore_{os.path.splitext(base_name)[0]}.csv")
    
    # C score 데이터 로드
    if not os.path.exists(c_score_file):
        print(f"오류: C score 파일이 존재하지 않습니다: {c_score_file}")
        print("먼저 CriticalityCalculator.py를 실행하여 C score를 계산해주세요.")
        exit(1)
    
    c_score_df = pd.read_csv(c_score_file)
    
    # C score 데이터와 원본 데이터 병합
    df = df.merge(c_score_df[['뉴스 식별자', 'criticality_score']], on='뉴스 식별자', how='left')
    
    # 키워드 기반 유사도 계산 (GPU 가속)
    similarity_matrix = calculate_keyword_similarity(df)
    
    # 영향력 점수 계산
    impact_scores = []
    for idx, row in df.iterrows():
        score, details = calculate_news_impact_score(df, row, similarity_matrix, idx)
        impact_scores.append({
            '일자': row['일자'],
            '제목': row['제목'],
            '언론사': row['언론사'],
            '대분류': row['대분류'],
            'impact_score': score,
            **details
        })
    
    # 결과를 DataFrame으로 변환
    impact_df = pd.DataFrame(impact_scores)
    
    # 영향력 점수 기준으로 정렬
    impact_df = impact_df.sort_values('impact_score', ascending=False)
    
    # 유사한 뉴스가 중복되지 않도록 상위 10개 뉴스 선정 (유사도 임계값 0.5로 낮춤)
    top_10_news = select_top_news(impact_df, similarity_matrix, similarity_threshold=0.5)
    
    # 결과 저장
    try:
        top_10_news.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"뉴스 영향력 분석 리포트가 저장되었습니다: {output_file}")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")
        print(f"저장 경로: {os.path.abspath(output_file)}")
        print(f"디렉토리 존재 여부: {os.path.exists(os.path.dirname(output_file))}")
        raise
    
    return output_file

if __name__ == "__main__":
    input_file = input("분석할 파일 경로를 입력하세요: ")
    if not os.path.exists(input_file):
        print(f"오류: 입력 파일이 존재하지 않습니다: {input_file}")
        exit(1)
    
    # 출력 파일 경로 설정
    output_file = os.path.join("NewsAnalysis/NewsImpactReports", f"NewsImpactReport_{os.path.basename(input_file)[:8]}.csv")
    
    generate_monthly_report(input_file, output_file) 