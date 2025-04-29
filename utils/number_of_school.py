import os
import pandas as pd

def count_schools_by_attributes(csv_folder_path: str, year: str = "2024") -> pd.DataFrame:
    """
    지정된 폴더 내의 2024년 관련 CSV 파일들에서 학교 수를 지역(시도), 학교급, 학교유형 등으로 세는 함수

    Args:
        csv_folder_path (str): CSV 파일이 있는 폴더 경로
        year (str): 사용할 연도 (기본값: "2024")

    Returns:
        pd.DataFrame: 시도/학교급/학교유형/계열별 학교 수 집계표
    """
    files = [
        f for f in os.listdir(csv_folder_path)
        if year in f and "결산" in f and "세입" in f and f.endswith(".csv")
    ]
    if not files:
        raise FileNotFoundError(f"{csv_folder_path}에 {year}년 파일이 없습니다.")

    dfs = []
    for f in files:
        df = pd.read_csv(os.path.join(csv_folder_path, f))
        if "초등" in f:
            school_level = "초등"
        elif "중등" in f:
            school_level = "중등"
        elif "고등" in f:
            school_level = "고등"
        else:
            school_level = "기타"
        df["학교급"] = school_level
        dfs.append(df)
    all_schools_df = pd.concat(dfs, ignore_index=True)

    all_schools_df = all_schools_df.drop_duplicates(subset=["SCHUL_CODE"])
    # '공립'과 '국립'을 '국공립'으로 통합
    all_schools_df["FOND_SC_CODE"] = all_schools_df["FOND_SC_CODE"].replace({"공립": "국공립", "국립": "국공립"})

    summary = all_schools_df.groupby(["ATPT_OFCDC_ORG_NM", "학교급", "FOND_SC_CODE"]).size().reset_index(name="학교 수")

    for level in ["초등", "중등", "고등"]:
        for fond_type in summary["FOND_SC_CODE"].unique():
            for edu in summary["ATPT_OFCDC_ORG_NM"].unique():
                condition = (
                    (summary["학교급"] == level) &
                    (summary["FOND_SC_CODE"] == fond_type) &
                    (summary["ATPT_OFCDC_ORG_NM"] == edu)
                )
                if not (condition).any():
                    summary = pd.concat([
                        summary,
                        pd.DataFrame([{
                            "ATPT_OFCDC_ORG_NM": edu,
                            "학교급": level,
                            "FOND_SC_CODE": fond_type,
                            "학교 수": 0,
                            "소계구분": ""
                        }])
                    ], ignore_index=True)

    # 소계 추가
    edu_office_subtotal = summary.groupby(["ATPT_OFCDC_ORG_NM"])["학교 수"].sum().reset_index()
    edu_office_subtotal["학교급"] = ""
    edu_office_subtotal["FOND_SC_CODE"] = ""
    edu_office_subtotal["소계구분"] = "교육청별 소계"

    level_subtotal = summary.groupby(["학교급"])["학교 수"].sum().reset_index()
    level_subtotal["ATPT_OFCDC_ORG_NM"] = "전체"
    level_subtotal["FOND_SC_CODE"] = ""
    level_subtotal["소계구분"] = "학교급별 소계"

    type_subtotal = summary.groupby(["FOND_SC_CODE"])["학교 수"].sum().reset_index()
    type_subtotal["ATPT_OFCDC_ORG_NM"] = "전체"
    type_subtotal["학교급"] = ""
    type_subtotal["소계구분"] = "학교유형별 소계"

    summary["소계구분"] = ""

    summary = pd.concat([summary, edu_office_subtotal, level_subtotal, type_subtotal], ignore_index=True)

    return summary

def main():
    csv_folder = "Database/schoolinfo/combined_csv"
    result = count_schools_by_attributes(csv_folder)
    # print(result)
    result.to_csv("Database/schoolinfo/number_of_school.csv", index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    main()
