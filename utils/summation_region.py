import os
import pandas as pd

import os
import pandas as pd

def summarize_budget_means_from_csv_folder(folder_path: str, output_dir: str, prefix: str):
    """
    시도교육청 단위 CSV 폴더 내 예산/결산, 세입/세출 파일들을 읽어
    평균을 요약한 뒤 output_dir에 private/public 접두어로 저장합니다.

    Args:
        folder_path (str): 예: Database/schoolinfo/private_filtered/강원특별자치도교육청
        output_dir (str): 예: Database/schoolinfo/summary/private_summary/강원특별자치도교육청
        prefix (str): 'private' 또는 'public'
    """
    os.makedirs(output_dir, exist_ok=True)

    세출_amt_column_map = {
        "AMT1": "인적자원_운용",
        "AMT2": "학생복지_교육격차해소",
        "AMT3": "기본적_교육활동",
        "AMT4": "선택적_교육활동",
        "AMT5": "교육활동_지원",
        "AMT6": "학교_일반운영",
        "AMT7": "학교_시설확충",
        "AMT8": "학교_재무활동",
        "YESAN_PER_HEAD": "1인당 평균 세출"
    }

    세입_amt_column_map = {
        "AMT1": "정부이전수입",
        "AMT2": "기타이전수입",
        "AMT3": "학부모부담수입",
        "AMT4": "미사용",
        "AMT5": "행정활동수입",
        "AMT6": "기타"
    }

    result_dict = {
        "예산_세입": [],
        "예산_세출": [],
        "결산_세입": [],
        "결산_세출": []
    }

    for filename in os.listdir(folder_path):
        if not filename.endswith(".csv"):
            continue

        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)

        # 예산/결산 판별
        if "예산" in filename:
            yosan_type = "예산"
        elif "결산" in filename:
            yosan_type = "결산"
        else:
            print(f"⚠️ 파일명에 '예산' 또는 '결산' 없음: {filename}")
            continue

        # 세입/세출 판별
        if "세입" in filename:
            amt_map = 세입_amt_column_map
            inout_type = "세입"
        elif "세출" in filename:
            amt_map = 세출_amt_column_map
            inout_type = "세출"
        else:
            print(f"⚠️ 파일명에 '세입' 또는 '세출' 없음: {filename}")
            continue

        key = f"{yosan_type}_{inout_type}"
        selected_cols = [col for col in amt_map if col in df.columns]

        row = {"파일명": filename}
        for col in selected_cols:
            row[amt_map[col]] = df[col].mean()
        row["평균합계"] = sum([row[amt_map[c]] for c in selected_cols])
        result_dict[key].append(row)

    # 저장
    for key, records in result_dict.items():
        if records:
            output_filename = f"{prefix}_{key}_요약.csv"
            output_path = os.path.join(output_dir, output_filename)
            summary_df = pd.DataFrame(records)
            summary_df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"✅ {output_filename} 저장 완료 → {output_path}")

def summarize_all_regions(base_input_dir: str, base_output_dir: str, prefix: str):
    """
    시도교육청별로 존재하는 모든 폴더에 대해 예산/결산, 세입/세출 요약을 생성합니다.

    Args:
        base_input_dir (str): 예: Database/schoolinfo/private_filtered/
        base_output_dir (str): 예: Database/schoolinfo/summary/private_summary/
        prefix (str): 'private' 또는 'public'
    """
    for region_name in os.listdir(base_input_dir):
        region_path = os.path.join(base_input_dir, region_name)
        if not os.path.isdir(region_path):
            continue

        output_path = os.path.join(base_output_dir, region_name)
        print(f"📂 처리 중: {region_name}")
        summarize_budget_means_from_csv_folder(
            folder_path=region_path,
            output_dir=output_path,
            prefix=prefix
        )

def main():
    # 사립학교 전체 시도교육청 요약
    summarize_all_regions(
        base_input_dir="Database/schoolinfo/private_filtered",
        base_output_dir="Database/schoolinfo/summary/private_summary",
        prefix="private"
    )

    # 국공립학교 전체 시도교육청 요약
    summarize_all_regions(
        base_input_dir="Database/schoolinfo/public_filtered",
        base_output_dir="Database/schoolinfo/summary/public_summary",
        prefix="public"
    )

    # 전체학교 전체 시도교육청 요약
    summarize_all_regions(
        base_input_dir="Database/schoolinfo/combined_filtered",
        base_output_dir="Database/schoolinfo/summary/combined_summary",
        prefix="combined"
    )

if __name__ == "__main__":
    main()