# 코드가 초기화되어 다시 정의해줍니다.

import os
import json
import pandas as pd

def save_school_budget_json_to_csv(json_path: str, csv_path: str):
    """
    학교 예산/결산 json 파일을 불러와서 DataFrame으로 변환 후 CSV로 저장합니다.
    
    Args:
        json_path (str): 원본 json 파일 경로
        csv_path (str): 저장할 csv 파일 경로
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("list", [])
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"✅ CSV 저장 완료: {csv_path}")


def batch_convert_json_to_csv(base_dir: str = "Database/schoolinfo"):
    """
    private, public 디렉토리 내 JSON 파일을 동일한 이름으로 CSV로 저장합니다.
    
    Args:
        base_dir (str): 기준 디렉토리 경로 (기본값은 "Database/schoolinfo")
    """
    categories = ["private", "public"]
    
    for category in categories:
        json_dir = os.path.join(base_dir, category)
        csv_dir = os.path.join(base_dir, f"{category}_csv")
        os.makedirs(csv_dir, exist_ok=True)

        for filename in os.listdir(json_dir):
            if filename.endswith(".json"):
                json_path = os.path.join(json_dir, filename)
                csv_path = os.path.join(csv_dir, filename.replace(".json", ".csv"))
                save_school_budget_json_to_csv(json_path, csv_path)

    print("✅ 모든 JSON → CSV 변환 완료")

def main():
    batch_convert_json_to_csv("Database/schoolinfo")

if __name__ == "__main__":
    main()