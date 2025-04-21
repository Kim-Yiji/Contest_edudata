import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import glob
import matplotlib.font_manager as fm

def load_monthly_data(base_dir, pattern):
    """월별 데이터 파일들을 로드하고 하나의 DataFrame으로 합침"""
    print(f"{pattern} 데이터 로드 중...")
    
    # 월별 파일 경로 찾기
    file_pattern = os.path.join(base_dir, f"*{pattern}*.csv")
    monthly_files = sorted(glob.glob(file_pattern))
    
    if not monthly_files:
        print(f"오류: {pattern} 파일이 존재하지 않습니다.")
        exit(1)
    
    # 모든 월별 데이터를 하나의 DataFrame으로 합침
    all_data = []
    for file in monthly_files:
        print(f"로드 중: {os.path.basename(file)}")
        df = pd.read_csv(file)
        all_data.append(df)
    
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"총 {len(monthly_files)}개의 월별 파일이 로드되었습니다.")
    return combined_df

def calculate_recency_score(news_date, latest_date):
    """연간 정규화된 Recency 점수 계산"""
    # 날짜 차이 계산
    days_diff = (latest_date - news_date).days
    
    # 연간 정규화 (1년 = 365일 기준)
    # 1월 1일 = 0점, 12월 31일 = 1점
    normalized_score = 1 - (days_diff / 365)
    
    # 최소 점수는 0.1로 설정 (과거 뉴스도 일정 가중치 부여)
    return max(normalized_score, 0.1)

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

def calculate_rfc_scores(classified_df, c_score_df):
    """RFC 점수 계산 및 시각화"""
    print("RFC 점수 계산 중...")
    
    # 데이터 병합
    print("데이터 병합 중...")
    df = classified_df.merge(
        c_score_df[['뉴스 식별자', 'criticality_score']], 
        on='뉴스 식별자', 
        how='left'
    )
    
    # 날짜 변환
    df['일자'] = pd.to_datetime(df['일자'])
    latest_date = df['일자'].max()
    
    # 대분류별 RFC 점수 계산
    rfc_scores = []
    categories = df['대분류'].unique()
    
    print("\n대분류별 점수 계산 중...")
    for category in categories:
        category_news = df[df['대분류'] == category]
        
        # Recency 점수 계산 (월간 정규화 방식)
        recency_scores = []
        for _, row in category_news.iterrows():
            news_date = pd.to_datetime(row['일자'])
            recency_score = calculate_recency_score(news_date, latest_date)
            recency_scores.append(recency_score)
        avg_recency = np.mean(recency_scores)
        
        # Frequency 점수 계산 (출처 다양성 + 지속성 고려)
        frequency_score, freq_details = calculate_frequency_score(category_news, df)
        
        # Criticality 점수 (C score)는 이미 계산되어 있음
        avg_criticality = category_news['criticality_score'].mean()
        
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
    
    return rfc_df

def plot_rfc_scores(rfc_df, output_file):
    """RFC 점수 시각화"""
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
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

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

    # 연도 입력 받기
    year = input("RFC 점수를 계산할 연도를 입력하세요 (예: 2024): ")
    
    # 출력 디렉토리 설정
    rfc_dir = "NewsAnalysis/RFCData/RFC_Score"
    os.makedirs(rfc_dir, exist_ok=True)
    
    # 출력 파일 경로 설정
    output_file = os.path.join(rfc_dir, f"RFCScore_{year}.csv")
    plot_file = os.path.join(rfc_dir, f"RFCScoreGraph_{year}.png")

    print(f"\n출력 파일: {output_file}")
    print(f"통계 그래프: {plot_file}\n")

    # Classified 데이터 로드
    classified_dir = "NewsAnalysis/NewsData/Classified"
    classified_df = load_monthly_data(classified_dir, f"Classified_{year}")
    
    # C Score 데이터 로드
    c_score_dir = "NewsAnalysis/RFCData/C_score"
    c_score_df = load_monthly_data(c_score_dir, f"CScore_{year}")
    
    # RFC 점수 계산 실행
    print("RFC 점수 계산 중...")
    rfc_scores = calculate_rfc_scores(classified_df, c_score_df)
    
    # 결과 저장
    rfc_scores.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # 그래프 생성 및 저장
    plot_rfc_scores(rfc_scores, plot_file)
    
    # 결과 출력
    print("\n=== 대분류별 RFC 점수 ===")
    print(rfc_scores) 