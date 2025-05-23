import os
import pandas as pd

def extract_school_level(filename: str, df: pd.DataFrame) -> str | None:
    if "학교급" in df.columns:
        return df["학교급"].iloc[0]
    elif "초등" in filename:
        return "초등"
    elif "중등" in filename:
        return "중등"
    elif "고등" in filename:
        return "고등"
    else:
        return None

def summarize_region_school_data(school_type: str, budget_type: str, revenue_type: str) -> None:
    """
    시도교육청 단위로 예산/결산 - 세입/세출 파일들을 요약하여 학교급별 평균 행 포함 CSV 파일 저장.

    Args:
        school_type (str): "private", "public", "combined" 중 하나
        budget_type (str): "예산" 또는 "결산"
        revenue_type (str): "세입" 또는 "세출"
    """

    시도교육청_목록 = [
        '강원특별자치도교육청', '경기도교육청', '경상남도교육청', '경상북도교육청', '광주광역시교육청', '대구광역시교육청',
        '대전광역시교육청', '부산광역시교육청', '서울특별시교육청', '세종특별자치시교육청', '울산광역시교육청',
        '인천광역시교육청', '전라남도교육청', '전북특별자치도교육청', '제주특별자치도교육청', '충청남도교육청',
        '충청북도교육청'
    ]

    for region in 시도교육청_목록:
        input_dir = f"Database/schoolinfo/{school_type}_filtered/{region}"
        output_dir = f"Database/schoolinfo/summary/{school_type}_summary/{region}"
        os.makedirs(output_dir, exist_ok=True)

        df_list = []

        for filename in os.listdir(input_dir):
            if budget_type in filename and revenue_type in filename and filename.endswith(".csv"):
                file_path = os.path.join(input_dir, filename)
                df = pd.read_csv(file_path)

                # 원하는 컬럼 매핑
                if revenue_type == "세입":
                    amt_column_map = {
                        "AMT1": "정부이전수입",
                        "AMT2": "기타이전수입",
                        "AMT3": "학부모부담수입",
                        "AMT4": "미사용",
                        "AMT5": "행정활동수입",
                        "AMT6": "기타"
                    }
                else:
                    amt_column_map = {
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

                # 변환된 컬럼으로 재구성
                selected_cols = [col for col in amt_column_map if col in df.columns]
                renamed_cols = {col: amt_column_map[col] for col in selected_cols}
                df = df[["학교급"] + selected_cols if "학교급" in df.columns else selected_cols]
                df.rename(columns=renamed_cols, inplace=True)

                # 학교급 추출
                school_level = extract_school_level(filename, df)
                if school_level is None:
                    print(f"⛔ 학교급 정보 없음 (컬럼/파일명 모두): {filename}")
                    continue

                numeric_cols = df.select_dtypes(include='number').columns
                mean_values = df[numeric_cols].sum()
                count = len(df)
                row = [filename] + mean_values.tolist() + [school_level, count]
                df_list.append(row)

        if df_list:
            columns = ["파일명"] + list(mean_values.index) + ["학교급", "학교 수"]
            summary_df = pd.DataFrame(df_list, columns=columns)

            # 학교급별 평균 행 추가
            avg_rows = []
            for school_level in summary_df["학교급"].unique():
                temp = summary_df[summary_df["학교급"] == school_level]
                weights = temp["학교 수"]
                weighted_avg = (temp.iloc[:, 1:-2].multiply(weights, axis=0).sum() / weights.sum())
                avg_row = [f"{school_level}_평균"] + weighted_avg.tolist() + [school_level, weights.sum()]
                avg_rows.append(avg_row)

            avg_df = pd.DataFrame(avg_rows, columns=columns)

            # 전체 평균 행 추가
            weights = summary_df["학교 수"]
            overall_weighted_avg = (summary_df.iloc[:, 1:-2].multiply(weights, axis=0).sum() / weights.sum())
            overall_avg_row = ["전체_평균"] + overall_weighted_avg.tolist() + ["전체", weights.sum()]
            overall_avg_df = pd.DataFrame([overall_avg_row], columns=columns)

            # 최종 결합
            final_df = pd.concat([summary_df, avg_df, overall_avg_df], ignore_index=True)

            output_filename = f"{school_type}_{budget_type}_{revenue_type}_요약.csv"
            output_path = os.path.join(output_dir, output_filename)
            final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✅ 저장 완료: {output_path}")
        else:
            print(f"⚠️ 데이터 없음: {region} - {school_type}_{budget_type}_{revenue_type}")


def main():
    for school_type in ["private", "public", "combined"]:
        for budget_type in ["예산", "결산"]:
            for revenue_type in ["세입", "세출"]:
                summarize_region_school_data(school_type, budget_type, revenue_type)


if __name__ == "__main__":
    main()