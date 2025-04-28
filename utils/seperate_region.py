# 코드 초기화로 인해 다시 정의해줍니다.

import os
import json

def filter_school_budget_by_org(base_dir="Database/schoolinfo"):
    """
    전국 교육청 목록을 기준으로 private/public 폴더 내 JSON 파일을 
    교육청별로 필터링하여 저장합니다.
    """
    # 전국 시도교육청 목록
    org_names = [
        "강원특별자치도교육청", "경기도교육청", "경상남도교육청", "경상북도교육청",
        "광주광역시교육청", "대구광역시교육청", "대전광역시교육청", "부산광역시교육청",
        "서울특별시교육청", "세종특별자치시교육청", "울산광역시교육청", "인천광역시교육청",
        "전라남도교육청", "전북특별자치도교육청", "제주특별자치도교육청", "충청남도교육청", "충청북도교육청"
    ]

    categories = ["private", "public"]

    for category in categories:
        src_dir = os.path.join(base_dir, category)

        for org in org_names:
            dest_dir = os.path.join(base_dir, f"{category}_filtered", org)
            os.makedirs(dest_dir, exist_ok=True)

            for filename in os.listdir(src_dir):
                if not filename.endswith(".json"):
                    continue

                src_path = os.path.join(src_dir, filename)

                try:
                    with open(src_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # 해당 교육청으로 필터링
                    filtered_list = [item for item in data.get("list", []) if item.get("ATPT_OFCDC_ORG_NM") == org]
                    filtered_data = {
                        "resultCode": "success",
                        "resultMsg": "성공",
                        "list": filtered_list
                    }

                    # 저장 파일명
                    dest_filename = f"{org}_{filename}"
                    dest_path = os.path.join(dest_dir, dest_filename)

                    with open(dest_path, "w", encoding="utf-8") as f:
                        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

                    print(f"✅ {dest_filename} 저장 완료 ({len(filtered_list)}개 항목)")

                except Exception as e:
                    print(f"❌ {filename} 처리 중 오류 발생: {e}")

import os
import pandas as pd

def redistribute_and_rename_csv_by_region(csv_root_dir: str):
    """
    csv_root_dir에 있는 CSV 파일들을 교육청 이름(앞부분) 기준으로 하위 폴더로 나누고,
    파일명을 '지역_종류_급별_예산or결산_세입or세출_연도.csv' 형식으로 바꿔 저장합니다.

    Args:
        csv_root_dir (str): 예) Database/schoolinfo/public_csv
    """
    files = [f for f in os.listdir(csv_root_dir) if f.endswith(".csv")]

    for filename in files:
        # 예: 경기도교육청_공립_고등_결산_세입_2022.csv
        parts = filename.replace(".csv", "").split("_")
        if len(parts) < 6:
            print(f"⚠️ 파일명 형식이 이상함: {filename}")
            continue

        region = parts[0]
        school_type = parts[1]  # 공립/사립
        level = parts[2]        # 고등/중등/초등
        budget_type = parts[3]  # 예산/결산
        io_type = parts[4]      # 세입/세출
        year = parts[5]         # 2022 등

        # 새로운 디렉토리 경로 및 파일 이름
        target_dir = os.path.join(region, csv_root_dir)
        os.makedirs(target_dir, exist_ok=True)

        new_filename = f"{region}_{school_type}_{level}_{budget_type}_{io_type}_{year}.csv"
        src_path = os.path.join(csv_root_dir, filename)
        dest_path = os.path.join(target_dir, new_filename)

        # 파일 저장
        df = pd.read_csv(src_path)
        df.to_csv(dest_path, index=False, encoding="utf-8-sig")

        print(f"✅ 저장 완료: {dest_path}")

    print("🎉 모든 CSV 지역별 정리 및 이름 변경 완료!")

def split_csv_by_education_office(csv_root_dir: str, office_colname: str = "ATPT_OFCDC_ORG_NM"):
    """
    모든 CSV 파일을 불러와서 시도교육청명(예: 경기도교육청) 기준으로 분리 저장합니다.
    예: 'Database/schoolinfo/private_csv' → 'Database/schoolinfo/private_filtered/경기도교육청/경기도교육청_파일명.csv'

    Args:
        csv_root_dir (str): CSV 파일이 들어있는 폴더
        office_colname (str): 교육청명을 담고 있는 컬럼명 (기본값은 ATPT_OFCDC_ORG_NM)
    """
    base_dir = os.path.dirname(csv_root_dir)  # 예: Database/schoolinfo
    filtered_name = os.path.basename(csv_root_dir).replace("_csv", "_filtered")  # 예: private_filtered
    target_root_dir = os.path.join(base_dir, filtered_name)

    files = [f for f in os.listdir(csv_root_dir) if f.endswith(".csv")]

    for filename in files:
        src_path = os.path.join(csv_root_dir, filename)
        try:
            df = pd.read_csv(src_path)

            if office_colname not in df.columns:
                print(f"⚠️ 컬럼 '{office_colname}' 이(가) 없음: {filename}")
                continue

            # 교육청별로 분리 저장
            for office_name, sub_df in df.groupby(office_colname):
                target_dir = os.path.join(target_root_dir, office_name)
                os.makedirs(target_dir, exist_ok=True)

                new_filename = f"{office_name}_{filename}"
                dest_path = os.path.join(target_dir, new_filename)
                sub_df.to_csv(dest_path, index=False, encoding="utf-8-sig")

                print(f"✅ {filename} → {office_name}/{new_filename} ({len(sub_df)}행 저장됨)")

        except Exception as e:
            print(f"❌ {filename} 처리 중 오류: {e}")

    print("🎉 CSV 파일 교육청 기준 분리 및 이름 변경 완료")

def main():
    split_csv_by_education_office("Database/schoolinfo/public_csv")
    split_csv_by_education_office("Database/schoolinfo/private_csv")
    split_csv_by_education_office("Database/schoolinfo/combined_csv")

if __name__ == "__main__":
    main()