import requests
import time

# ▶︎ FastAPI 서버 주소
BASE_URL = "http://localhost:8000"

# ▶︎ API 경로
ENDPOINTS = {
    "공립": "/schoolinfo/budget",
    "사립": "/privateschool/budget"
}

# ▶︎ 요청 조합
years = [2022, 2023, 2024]
school_levels = {
    "02": "초등",
    "03": "중등",
    "04": "고등"
}
depth_no = {
    "10": "예산",
    "20": "결산"
}
depth_no2 = {
    "1": "세입",
    "2": "세출",
    "3": "세입",
    "4": "세출"
}

def send_all_requests():
    for school_type, endpoint in ENDPOINTS.items():
        print(f"\n📦 {school_type} API 요청 시작")
        for year in years:
            for schul_code in school_levels.keys():
                for d1 in depth_no.keys():
                    for d2 in depth_no2.keys():
                        payload = {
                            "pbanYr": year,
                            "schulKndCode": schul_code,
                            "depthNo": d1,
                            "depthNo2": d2
                        }
                        try:
                            res = requests.post(BASE_URL + endpoint, json=payload)
                            if res.status_code == 200:
                                print(f"✅ [{school_type}] 저장 완료: {payload}")
                            else:
                                print(f"❌ [{school_type}] 실패: {payload} - 상태코드 {res.status_code}")
                        except Exception as e:
                            print(f"⚠️ [{school_type}] 예외 발생: {payload} - {e}")
                        time.sleep(0.2)  # 서버 부하 방지

if __name__ == "__main__":
    send_all_requests()