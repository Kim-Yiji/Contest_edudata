import pandas as pd
import re
from tqdm import tqdm
import os

def clean_text(text):
    """텍스트 정제 함수"""
    if pd.isna(text):
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수문자 제거 (한글, 영문, 숫자, 공백만 남김)
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    
    # 연속된 공백을 하나로 통일
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def preprocess_news_data(input_file, output_file):
    """뉴스 데이터 전처리 함수"""
    print("뉴스 데이터 로딩 중...")
    df = pd.read_csv(input_file, encoding='utf-8')
    initial_count = len(df)
    print(f"초기 데이터 개수: {initial_count:,}개")
    
    print("\n불필요한 열 제거 중...")
    # 제거할 열 목록
    columns_to_drop = [
        '기고자', '통합 분류1', '통합 분류2', '통합 분류3',
        '사건/사고 분류1', '사건/사고 분류2', '사건/사고 분류3',
        '인물', '위치', '기관', '본문', '분석제외 여부'
    ]
    
    # 존재하는 열만 제거
    existing_columns = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=existing_columns)
    print(f"제거된 열: {', '.join(existing_columns)}")
    
    print("\n데이터 전처리 중...")
    # 텍스트 정제
    df['제목'] = df['제목'].apply(clean_text)
    df['키워드'] = df['키워드'].apply(clean_text)
    
    # 중복 기사 제거 (제목 기준)
    print("\n중복 기사 제거 중...")
    duplicate_count = df.duplicated(subset=['제목']).sum()
    df = df.drop_duplicates(subset=['제목'], keep='first')
    final_count = len(df)
    print(f"제거된 중복 기사: {duplicate_count:,}개")
    print(f"최종 남은 기사: {final_count:,}개")
    
    # 결과 저장
    print("\n결과 저장 중...")
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print("\n=== 전처리 결과 요약 ===")
    print(f"초기 데이터 개수: {initial_count:,}개")
    print(f"제거된 중복 기사: {duplicate_count:,}개")
    print(f"최종 남은 기사: {final_count:,}개")
    print(f"전체 제거된 기사: {initial_count - final_count:,}개")
    print(f"제거된 열: {', '.join(existing_columns)}")
    
    return df

if __name__ == "__main__":
    # 사용자 입력 받기
    input_file = input("전처리할 데이터의 파일 경로를 입력하세요 (예: NewsAnalysis/NewsData/Raw/20250312-20250412.csv): ")
    
    # 입력 파일 존재 여부 확인
    if not os.path.exists(input_file):
        print(f"오류: 입력 파일이 존재하지 않습니다: {input_file}")
        exit(1)
    
    # 출력 디렉토리 설정
    preprocessed_dir = "NewsAnalysis/NewsData/Preprocessed"
    os.makedirs(preprocessed_dir, exist_ok=True)
    
    # 입력 파일명에서 날짜 추출
    date_match = re.search(r'\d{8}-\d{8}', input_file)
    if date_match:
        date_str = date_match.group()
        output_file = os.path.join(preprocessed_dir, f"Preprocessed_{date_str}.csv")
    else:
        # 날짜가 없는 경우 원본 파일명 사용
        base_name = os.path.basename(input_file)
        output_file = os.path.join(preprocessed_dir, f"Preprocessed_{base_name}")
    
    print(f"\n입력 파일: {input_file}")
    print(f"출력 파일: {output_file}")
    
    preprocess_news_data(input_file, output_file) 