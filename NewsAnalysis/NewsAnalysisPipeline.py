import os
import re
from datetime import datetime, timedelta
from NewsPreprocessor import preprocess_news_data
from NewsClassifier import classify_news
from RFCCalculator.CriticalityCalculator import calculate_and_save_criticality_scores
from NewsImpactAnalyzer import generate_monthly_report

def get_monthly_files(start_date, raw_dir):
    """시작 날짜부터 마지막 파일까지의 월별 파일 목록을 가져옴"""
    files = []
    current_date = start_date
    
    while True:
        # 월의 첫날과 마지막날 계산
        first_day = current_date.replace(day=1)
        if current_date.month == 12:
            last_day = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        # 파일명 형식: YYYYMMDD-YYYYMMDD.csv
        file_name = f"{first_day.strftime('%Y%m%d')}-{last_day.strftime('%Y%m%d')}.csv"
        file_path = os.path.join(raw_dir, file_name)
        
        if not os.path.exists(file_path):
            break
            
        files.append(file_path)
        
        # 다음 달로 이동
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return files

def run_analysis_pipeline(input_file):
    """전체 분석 파이프라인 실행"""
    try:
        # 입력 파일 존재 여부 확인
        if not os.path.exists(input_file):
            print(f"오류: 입력 파일이 존재하지 않습니다: {input_file}")
            return False

        # 날짜 추출
        date_match = re.search(r'\d{8}-\d{8}', input_file)
        if not date_match:
            print("오류: 파일명에서 날짜를 추출할 수 없습니다.")
            return False
        date_str = date_match.group()

        print(f"\n=== {date_str} 기간 데이터 분석 시작 ===")

        # 1단계: 전처리
        print("\n=== 1단계: 뉴스 데이터 전처리 ===")
        preprocessed_file = f"NewsAnalysis/NewsData/Preprocessed/Preprocessed_{date_str}.csv"
        preprocess_news_data(input_file, preprocessed_file)
        print(f"전처리 완료: {preprocessed_file}")

        # 2단계: 분류
        print("\n=== 2단계: 뉴스 분류 ===")
        classified_file = f"NewsAnalysis/NewsData/Classified/Classified_{date_str}.csv"
        classify_news(preprocessed_file, classified_file)
        print(f"분류 완료: {classified_file}")

        # 3단계: 중요도 점수 계산
        print("\n=== 3단계: 중요도 점수 계산 ===")
        calculate_and_save_criticality_scores(classified_file)
        cscore_file = f"NewsAnalysis/RFCData/C_score/CScore_{date_str}.csv"
        print(f"중요도 점수 계산 완료: {cscore_file}")

        # 4단계: 뉴스 영향력 분석
        print("\n=== 4단계: 뉴스 영향력 분석 ===")
        impact_report_file = f"NewsAnalysis/NewsImpactReports/NewsImpactReport_{date_str}.csv"
        generate_monthly_report(classified_file, impact_report_file)
        print(f"영향력 분석 완료: {impact_report_file}")

        print(f"\n=== {date_str} 기간 분석 완료 ===")
        print(f"전처리 결과: {preprocessed_file}")
        print(f"분류 결과: {classified_file}")
        print(f"중요도 점수: {cscore_file}")
        print(f"영향력 분석: {impact_report_file}")
        
        return True
        
    except Exception as e:
        print(f"\n오류 발생: {input_file}")
        print(f"오류 내용: {str(e)}")
        print(f"오류 발생 위치: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
        return False

def process_monthly_data():
    """월별 데이터 자동 처리"""
    # 사용자 입력 받기
    while True:
        try:
            input_str = input("분석할 기간을 입력하세요 (예: 202303-202304): ")
            start_year_month, end_year_month = input_str.split('-')
            
            # 시작 연월 검증
            if len(start_year_month) != 6:
                raise ValueError("시작 연월은 6자리 숫자여야 합니다.")
            start_year = int(start_year_month[:4])
            start_month = int(start_year_month[4:])
            if start_month < 1 or start_month > 12:
                raise ValueError("시작 월은 1부터 12 사이여야 합니다.")
            
            # 종료 연월 검증
            if len(end_year_month) != 6:
                raise ValueError("종료 연월은 6자리 숫자여야 합니다.")
            end_year = int(end_year_month[:4])
            end_month = int(end_year_month[4:])
            if end_month < 1 or end_month > 12:
                raise ValueError("종료 월은 1부터 12 사이여야 합니다.")
            
            # 시작일과 종료일 생성
            start_date = datetime(start_year, start_month, 1)
            if end_month == 12:
                end_date = datetime(end_year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(end_year, end_month + 1, 1) - timedelta(days=1)
            
            # 시작일이 종료일보다 늦은 경우
            if start_date > end_date:
                raise ValueError("시작 연월이 종료 연월보다 늦을 수 없습니다.")
                
            break
        except ValueError as e:
            print(f"잘못된 입력입니다: {str(e)}")
            print("올바른 형식으로 다시 입력해주세요.")
    
    # Raw 데이터 디렉토리
    raw_dir = "NewsAnalysis/NewsData/Raw"
    
    # 처리할 파일 목록 가져오기
    files = []
    current_date = start_date
    
    while current_date <= end_date:
        # 월의 첫날과 마지막날 계산
        first_day = current_date.replace(day=1)
        if current_date.month == 12:
            last_day = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        
        # 파일명 형식: YYYYMMDD-YYYYMMDD.csv
        file_name = f"{first_day.strftime('%Y%m%d')}-{last_day.strftime('%Y%m%d')}.csv"
        file_path = os.path.join(raw_dir, file_name)
        
        if os.path.exists(file_path):
            files.append(file_path)
        
        # 다음 달로 이동
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    if not files:
        print(f"{start_year_month}부터 {end_year_month}까지의 데이터 파일이 없습니다.")
        return
    
    print(f"\n총 {len(files)}개의 월별 데이터를 처리합니다.")
    
    # 각 파일 처리
    success_count = 0
    for file_path in files:
        print(f"\n{'='*50}")
        print(f"파일 처리 중: {os.path.basename(file_path)}")
        print(f"{'='*50}")
        
        if not run_analysis_pipeline(file_path):
            print(f"\n{os.path.basename(file_path)} 파일 처리 중 오류가 발생했습니다.")
            print("프로그램을 종료합니다.")
            return
        
        success_count += 1
    
    print(f"\n{'='*50}")
    print(f"처리 완료: {success_count}/{len(files)}개 파일 성공")
    print(f"{'='*50}")

if __name__ == "__main__":
    process_monthly_data() 