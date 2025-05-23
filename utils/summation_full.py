import os
import pandas as pd
import re

def summarize_budget_means_from_csv_folder(folder_path: str, output_dir: str):
    """
    폴더 내 CSV 파일들을 예산/결산, 세입/세출로 분류하여 각각 평균 요약을 저장합니다.
    저장 파일명 앞에는 public/private 구분이 포함됩니다.

    Args:
        folder_path (str): CSV 파일들이 있는 폴더 경로
        output_dir (str): 요약된 결과를 저장할 디렉토리
    """
    os.makedirs(output_dir, exist_ok=True)

    # 폴더 이름에서 public/private 추출
    prefix = os.path.basename(folder_path).replace("_csv", "")  # 예: private_csv → private

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

        if "예산" in filename:
            yosan_type = "예산"
        elif "결산" in filename:
            yosan_type = "결산"
        else:
            print(f"⚠️ 파일명에 '예산' 또는 '결산' 없음: {filename}")
            continue

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
        
        # 학교급 정보 추출
        school_level_match = re.search(r"(초등|중등|고등)", filename)
        row["학교급"] = school_level_match.group(1) if school_level_match else None
        result_dict[key].append(row)

    # 저장
    for key, records in result_dict.items():
        if records:
            output_filename = f"{prefix}_{key}_요약.csv"  # 여기서 prefix 추가됨!
            output_path = os.path.join(output_dir, output_filename)
            # 평균 행 추가 (학교급별 및 전체)
            school_level_frames = {"초등": [], "중등": [], "고등": []}
            for record in result_dict[key]:
                level = record.get("학교급")
                if level in school_level_frames:
                    school_level_frames[level].append(record)

            avg_rows = []
            for level, records in school_level_frames.items():
                if records:
                    df_level = pd.DataFrame(records)
                    mean_vals = df_level.drop(columns=["파일명", "학교급"]).mean()
                    avg_row = {"파일명": f"{prefix}_{key}_{level}_평균", "학교급": level}
                    avg_row.update(mean_vals.to_dict())
                    avg_rows.append(avg_row)

            # 전체 평균
            df_all = pd.DataFrame(result_dict[key])
            mean_total = df_all.drop(columns=["파일명", "학교급"]).mean()
            avg_total_row = {"파일명": f"{prefix}_{key}_전체_평균", "학교급": "전체"}
            avg_total_row.update(mean_total.to_dict())
            avg_rows.append(avg_total_row)

            # 최종 결과 저장
            df_final = pd.concat([df_all, pd.DataFrame(avg_rows)], ignore_index=True)
            df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"✅ {output_filename} 저장 완료 → {output_path}")

def summarize_total_and_school_level_mean(input_dir: str, output_dir: str, prefix: str):
    """
    예산/결산, 세입/세출을 모두 포함한 private/public 데이터를 합쳐
    전체 평균과 학교급별 평균을 구해 summary 폴더에 저장

    Args:
        input_dir (str): private_summary 또는 public_summary 폴더 경로
        output_dir (str): 저장할 summary 폴더 경로
        prefix (str): 'private' 또는 'public'
    """
    all_files = [f for f in os.listdir(input_dir) if f.endswith(".csv")]
    df_list = []

    for fname in all_files:
        path = os.path.join(input_dir, fname)
        df = pd.read_csv(path)
        df["학교급"] = df["파일명"].str.extract(r"_(초등|중등|고등)_")[0]
        df_list.append(df)

    # 모든 데이터 합치기
    df_all = pd.concat(df_list, ignore_index=True)

    # 수치 컬럼만 추출
    value_columns = [col for col in df_all.columns if col not in ["파일명", "학교급"]]

    # ✅ 전체 평균 계산
    total_mean = df_all[value_columns].mean()
    total_mean_row = {"파일명": f"{prefix}_전체평균"}
    total_mean_row.update(total_mean)
    df_total = pd.DataFrame([total_mean_row])

    # ✅ 학교급별 평균 계산
    school_rows = []
    for level in ["초등", "중등", "고등"]:
        sub_df = df_all[df_all["학교급"] == level]
        if not sub_df.empty:
            mean_row = {"파일명": f"{prefix}_{level}_평균"}
            mean_row.update(sub_df[value_columns].mean())
            school_rows.append(mean_row)
    df_school = pd.DataFrame(school_rows)

    # ✅ 저장
    os.makedirs(output_dir, exist_ok=True)
    df_total.to_csv(os.path.join(output_dir, f"{prefix}_전체평균_요약.csv"), index=False, encoding="utf-8-sig")
    df_school.to_csv(os.path.join(output_dir, f"{prefix}_학교급별_평균_요약.csv"), index=False, encoding="utf-8-sig")
    print(f"✅ {prefix} 전체/학교급 평균 요약 저장 완료")

def combine_public_private_summary_and_average(
    private_dir: str,
    public_dir: str,
    output_dir: str
):
    """
    private & public 요약 파일을 병합하여 각 예산/결산 - 세입/세출 별 평균을 구해 저장합니다.

    Args:
        private_dir (str): private 요약 파일 폴더
        public_dir (str): public 요약 파일 폴더
        output_dir (str): 저장할 폴더
    """
    os.makedirs(output_dir, exist_ok=True)

    combinations = ["예산_세입", "예산_세출", "결산_세입", "결산_세출"]

    for combo in combinations:
        private_path = os.path.join(private_dir, f"private_{combo}_요약.csv")
        public_path = os.path.join(public_dir, f"public_{combo}_요약.csv")

        if not os.path.exists(private_path) or not os.path.exists(public_path):
            print(f"⚠️ {combo} 파일 없음 → 스킵")
            continue

        # 파일 읽기
        df_private = pd.read_csv(private_path)
        df_public = pd.read_csv(public_path)

        # 학교급 정보 추출
        df_private["학교급"] = df_private["파일명"].str.extract(r"_(초등|중등|고등)_")[0]
        df_public["학교급"] = df_public["파일명"].str.extract(r"_(초등|중등|고등)_")[0]

        # 병합
        df_combined = pd.concat([df_private, df_public], ignore_index=True)

        # 평균 계산
        value_cols = [col for col in df_combined.columns if col not in ["파일명", "학교급"]]
        row = {"파일명": f"combined_{combo}_평균"}
        for col in value_cols:
            row[col] = df_combined[col].mean()

        # 저장
        df_output = pd.DataFrame([row])
        output_path = os.path.join(output_dir, f"combined_{combo}_요약.csv")
        df_output.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"✅ 저장 완료: {output_path}")

def main():
    summarize_budget_means_from_csv_folder(
        folder_path="Database/schoolinfo/private_csv",
        output_dir="Database/schoolinfo/summary/private_summary"
    )
    summarize_budget_means_from_csv_folder(
        folder_path="Database/schoolinfo/public_csv",
        output_dir="Database/schoolinfo/summary/public_summary"
    )
    summarize_budget_means_from_csv_folder(
        folder_path="Database/schoolinfo/combined_csv",
        output_dir="Database/schoolinfo/summary/combined_summary"
    )

if __name__ == "__main__":
    main()