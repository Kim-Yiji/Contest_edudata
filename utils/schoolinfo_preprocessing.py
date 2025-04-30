import json
import pandas as pd
import os

def save_school_budget_json_to_csv(json_path: str, csv_path: str):
    """
    예결산 JSON 파일을 불러와서 학교별 항목을 DataFrame으로 변환한 뒤 CSV로 저장합니다.
    
    Args:
        json_path (str): 입력 JSON 파일 경로
        csv_path (str): 출력 CSV 파일 경로
    """
    # JSON 파일 로드
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # list 안의 데이터만 추출
    school_data = data.get("list", [])
    
    # DataFrame으로 변환
    df = pd.DataFrame(school_data)

    # CSV로 저장
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ CSV 저장 완료: {csv_path}")

def rename_common(csv_path: str):
    """
    예산 세입/세출 데이터에서 공통 컬럼명을 한글로 변경하고,
    같은 경로에 덮어써 저장합니다.

    Args:
        csv_path (str): 처리할 CSV 파일 경로
    """
    공통_column_map = {
        "FOND_SC_CODE": "설립구분",
        "SCHUL_KND_SC_CODE": "학교급코드",
        "ADRCD_NM": "주소",
        "JU_ORG_NM": "교육지원청명",
        "ATPT_OFCDC_ORG_NM": "시도교육청명",
        "JU_ORG_CODE": "교육지원청코드",
        "PBAN_EXCP_YN": "예외여부",
        "FAS_DTN_SC_CODE": "회계기준구분",
        "PBAN_REV_EX_SC_CODE": "예결산_항목유형",
        "SCHUL_CODE": "학교코드",
        "ATPT_OFCDC_ORG_CODE": "시도교육청코드",
        "LCTN_SC_CODE": "지역코드",
        "HS_KND_SC_NM": "고교유형",
        "BNHH_YN": "분교여부",
        "SCHUL_NM": "학교명",
        "SCHUL_CRSE_SC_VALUE_NM": "학교과정명",
        "SCHUL_CRSE_SC_VALUE": "학교과정코드",
        "PBAN_EXCP_RSN": "예외이유"  
    }

    # CSV 파일 불러오기
    df = pd.read_csv(csv_path)

    # 컬럼명 변경
    df.rename(columns=공통_column_map, inplace=True)

    # 덮어쓰기 저장
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ 공통 컬럼 한글로 저장 완료: {csv_path}")

def rename_out(csv_path: str):
    """
    주어진 CSV 파일에서 예산 세출 AMT1~AMT8 컬럼명을 한글로 변경하고,
    원래 파일 경로에 덮어써 저장합니다.

    Args:
        csv_path (str): 처리할 CSV 파일 경로
    """
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

    # CSV 파일 불러오기
    df = pd.read_csv(csv_path)

    # 컬럼명 변경
    df.rename(columns=amt_column_map, inplace=True)

    # 원래 파일에 덮어쓰기
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ 한글 컬럼명으로 저장 완료: {csv_path}")

def rename_in(csv_path: str):
    """
    주어진 CSV 파일에서 예산 세입 AMT1~AMT6 컬럼명을 한글로 변경하고,
    원래 파일 경로에 덮어써 저장합니다.

    Args:
        csv_path (str): 처리할 CSV 파일 경로
    """
    amt_column_map = {
        "AMT1": "정부이전수입",
        "AMT2": "기타이전수입",
        "AMT3": "학부모부담수입",
        "AMT4": "미사용",
        "AMT5": "행정활동수입",
        "AMT6": "기타"
    }

    # CSV 파일 불러오기
    df = pd.read_csv(csv_path)

    # 컬럼명 변경
    df.rename(columns=amt_column_map, inplace=True)

    # 원래 파일에 덮어쓰기
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ 한글 컬럼명으로 저장 완료: {csv_path}")

def process_school_budget_folder(input_folder: str, output_folder: str):
    """
    지정된 폴더 내의 JSON 예산 파일들을 세입/세출 여부에 따라 적절한 CSV로 변환하고,
    컬럼명을 각각 한글로 바꿔 저장합니다.

    Args:
        input_folder (str): 원본 JSON 파일들이 들어 있는 폴더 경로
        output_folder (str): 처리된 CSV 파일이 저장될 폴더 경로
    """
    # 파일 목록 불러오기
    files = os.listdir(input_folder)

    for filename in files:
        if not filename.endswith(".json"):
            continue

        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # 1. JSON → CSV 저장
        save_school_budget_json_to_csv(input_path, output_path)

        # 2. 세입 or 세출 구분
        if "세입" in filename:
            rename_in(output_path)
        elif "세출" in filename:
            rename_out(output_path)

        # 3. 공통 컬럼명 변경
        rename_common(output_path)

    print("✅ 모든 파일 처리 완료!")