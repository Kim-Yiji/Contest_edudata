import json
import pandas as pd

def extract_school_org_mapping_from_json(json_path: str, output_csv_path: str) -> None:
    """
    JSON 파일에서 학교 코드와 교육청 정보를 추출하여 CSV로 저장합니다.
    
    Args:
        json_path (str): 입력 JSON 파일 경로
        output_csv_path (str): 저장할 CSV 경로
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    school_list = data.get("list", [])
    
    df = pd.DataFrame(school_list)[["SCHUL_CODE", "ATPT_OFCDC_ORG_NM", "SCHUL_NM"]].dropna()
    df = df.drop_duplicates(subset="SCHUL_CODE")

    df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ 매핑 CSV 저장 완료: {output_csv_path}")


def fill_org_info_by_school_code(input_csv_path: str, mapping_csv_path: str, output_csv_path: str) -> None:
    """
    교육청 정보가 누락된 CSV에 학교 코드 기준으로 교육청 정보를 채워 넣습니다.
    
    Args:
        input_csv_path (str): 교육청 정보가 누락된 원본 CSV 경로
        mapping_csv_path (str): 'SCHUL_CODE'와 'ATPT_OFCDC_ORG_NM'이 포함된 매핑 CSV 경로
        output_csv_path (str): 병합된 결과를 저장할 CSV 경로
    """
    df_target = pd.read_csv(input_csv_path, encoding="cp949")
    df_lookup = pd.read_csv(mapping_csv_path)

    # merge
    df_merged = df_target.merge(df_lookup, left_on="학교명", right_on="SCHUL_NM", how="left")
    # df_merged = df_target.merge(df_lookup, left_on="학교코드", right_on="SCHUL_CODE", how="left")

    df_merged.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ 교육청 정보 병합 완료: {output_csv_path}")

def main():
    # 파일 경로 설정
    json_input_path = "Database/schoolinfo/private/사립_고등_결산_세입_2022.json"           # JSON 파일 경로
    mapping_csv_path = "Database/etc/school_region_mapping_table.csv"               # 추출된 매핑 테이블 CSV 경로
    csv_with_missing_org = "Database/etc/0205.급식비집행실적(09-24)(100%).csv"             # 교육청 정보가 없는 CSV 경로
    csv_filled_output_path = "Database/etc/0205.급식비집행실적(09-24)(100%)_filled.csv"            # 최종 병합된 결과 저장 경로

    # 1단계: 매핑 테이블 생성
    extract_school_org_mapping_from_json(json_input_path, mapping_csv_path)

    # 2단계: 교육청 정보 병합
    fill_org_info_by_school_code(csv_with_missing_org, mapping_csv_path, csv_filled_output_path)


if __name__ == "__main__":
    main()