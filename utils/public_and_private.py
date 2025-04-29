import os
import pandas as pd

def merge_common_csv_rows(public_dir: str, private_dir: str, output_dir: str):
    """
    공립과 사립 CSV 파일에서 앞부분(공립/사립)을 제외한 동일한 파일명을 기준으로 행 데이터를 병합하여 저장합니다.
    
    Args:
        public_dir (str): 공립 CSV가 들어있는 폴더
        private_dir (str): 사립 CSV가 들어있는 폴더
        output_dir (str): 병합된 CSV를 저장할 폴더
    """
    os.makedirs(output_dir, exist_ok=True)

    # 파일명 매칭용 딕셔너리
    file_map = {}

    def collect_files(folder, tag):
        for file in os.listdir(folder):
            if not file.endswith(".csv"):
                continue
            short_name = "_".join(file.split("_")[1:])  # 앞에 '공립' 또는 '사립' 제거
            full_path = os.path.join(folder, file)
            file_map.setdefault(short_name, []).append(full_path)

    collect_files(public_dir, "공립")
    collect_files(private_dir, "사립")

    for short_name, paths in file_map.items():
        dfs = []
        for path in paths:
            try:
                df = pd.read_csv(path)
                dfs.append(df)
            except Exception as e:
                print(f"⚠️ {path} 읽기 실패: {e}")

        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            output_path = os.path.join(output_dir, short_name)
            combined_df.to_csv(output_path, index=False, encoding="utf-8-sig")
            print(f"✅ 병합 저장: {output_path}")

    print("🎉 모든 병합 완료")

def main():
    merge_common_csv_rows(
        public_dir="Database/schoolinfo/public_csv",
        private_dir="Database/schoolinfo/private_csv",
        output_dir="Database/schoolinfo/combined_csv"
    )

if __name__ == "__main__":
    main()