import os
import json
from datetime import datetime

def save_json(data: dict, folder: str, filename: str) -> None:
    """
    데이터를 지정한 폴더에 JSON으로 저장
    - folder: 저장할 폴더 경로 (ex: "Database/schoolinfo")
    - filename: 저장 파일 이름 (ex: "초등_예산_세입_2023.json")
    """
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)