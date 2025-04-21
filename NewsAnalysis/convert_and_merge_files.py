import os
import pandas as pd
from datetime import datetime
import calendar

def convert_and_merge_files():
    # Raw 폴더 경로
    raw_dir = "NewsAnalysis/NewsData/Raw"
    
    # 모든 xlsx 파일 찾기
    xlsx_files = [f for f in os.listdir(raw_dir) if f.endswith('.xlsx') and f.startswith('NewsResult_')]
    
    print(f"총 {len(xlsx_files)}개의 xlsx 파일을 처리합니다.")
    
    # 월별로 파일 그룹화
    monthly_files = {}
    for xlsx_file in xlsx_files:
        try:
            # 날짜 추출 (예: 20230101-20230131)
            date_str = xlsx_file.replace('NewsResult_', '').replace('.xlsx', '')
            year = int(date_str[:4])
            month = int(date_str[4:6])
            year_month = f"{year}{month:02d}"
            
            if year_month not in monthly_files:
                monthly_files[year_month] = []
            monthly_files[year_month].append(xlsx_file)
            
        except Exception as e:
            print(f"파일명 파싱 오류: {xlsx_file}")
            print(f"오류 내용: {str(e)}")
            continue
    
    # 각 월별로 처리
    for year_month, files in monthly_files.items():
        year = int(year_month[:4])
        month = int(year_month[4:])
        print(f"\n=== {year}년 {month}월 파일 처리 중 ===")
        
        # 해당 월의 모든 파일을 하나의 데이터프레임으로 통합
        merged_df = pd.DataFrame()
        
        for xlsx_file in files:
            try:
                # 원본 파일 경로
                xlsx_path = os.path.join(raw_dir, xlsx_file)
                
                print(f"변환 중: {xlsx_file}")
                
                # xlsx 파일 읽기
                df = pd.read_excel(xlsx_path)
                
                # 데이터프레임에 추가
                merged_df = pd.concat([merged_df, df], ignore_index=True)
                
                # 원본 xlsx 파일 삭제
                os.remove(xlsx_path)
                print(f"원본 파일 삭제: {xlsx_file}")
                
            except Exception as e:
                print(f"오류 발생: {xlsx_file}")
                print(f"오류 내용: {str(e)}")
                continue
        
        if not merged_df.empty:
            # 해당 월의 마지막 날짜 계산
            last_day = calendar.monthrange(year, month)[1]
            
            # 통합된 파일 저장
            output_file = f"{year_month}01-{year_month}{last_day:02d}.csv"
            output_path = os.path.join(raw_dir, output_file)
            
            merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"통합 완료: {output_file}")
            print(f"총 {len(merged_df)}개의 행이 저장되었습니다.")

if __name__ == "__main__":
    convert_and_merge_files() 