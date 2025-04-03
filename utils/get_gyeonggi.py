import os
import json

# 기준 디렉토리
BASE_DIR = "Database/schoolinfo"
TARGET_ORG_NAME = "경기도교육청"

# 처리할 두 폴더
categories = ["private", "public"]

for category in categories:
    src_dir = os.path.join(BASE_DIR, category)
    dest_dir = os.path.join(BASE_DIR, f"{category}_filtered")

    # 출력 디렉토리 생성
    os.makedirs(dest_dir, exist_ok=True)

    for filename in os.listdir(src_dir):
        if filename.endswith(".json"):
            src_path = os.path.join(src_dir, filename)

            try:
                with open(src_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 필터링
                filtered_list = [item for item in data.get("list", []) if item.get("ATPT_OFCDC_ORG_NM") == TARGET_ORG_NAME]
                filtered_data = {
                    "resultCode": "success",
                    "resultMsg": "성공",
                    "list": filtered_list
                }

                # 저장 경로 및 파일명 변경
                dest_filename = f"경기_{filename}"
                dest_path = os.path.join(dest_dir, dest_filename)

                with open(dest_path, "w", encoding="utf-8") as f:
                    json.dump(filtered_data, f, ensure_ascii=False, indent=2)

                print(f"✅ {dest_filename} 저장 완료 ({len(filtered_list)}개 항목)")

            except Exception as e:
                print(f"❌ {filename} 처리 중 오류 발생: {e}")