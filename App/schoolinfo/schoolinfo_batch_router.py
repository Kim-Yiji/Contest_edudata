from fastapi import APIRouter, Query
import requests
import time

router = APIRouter(prefix="/schoolinfo", tags=["Batch Download"])

BASE_URL = "http://localhost:8000"
ENDPOINTS = {
    "public": "/publicschool/budget",
    "private": "/privateschool/budget"
}

@router.post("/batch")
def run_batch_download(type: str = Query("both", enum=["public", "private", "both"])):
    count = 0
    failed = []
    start = time.time()

    years = [2022, 2023, 2024]
    schul_codes = ["02", "03", "04"]
    depth1 = ["10", "20"]
    depth2 = ["1", "2", "3", "4"]

    types_to_run = ["public", "private"] if type == "both" else [type]

    for school_type in types_to_run:
        print(f"\n📦 {school_type.upper()} 요청 시작")
        endpoint = BASE_URL + ENDPOINTS[school_type]

        for year in years:
            for code in schul_codes:
                for d1 in depth1:
                    for d2 in depth2:
                        payload = {
                            "pbanYr": year,
                            "schulKndCode": code,
                            "depthNo": d1,
                            "depthNo2": d2
                        }
                        try:
                            res = requests.post(endpoint, json=payload)
                            if res.status_code == 200:
                                print(f"✅ 저장 성공: {school_type} | {payload}")
                                count += 1
                            else:
                                print(f"❌ 저장 실패: {school_type} | {payload} | 상태코드: {res.status_code}")
                                failed.append({"type": school_type, "payload": payload, "status": res.status_code})
                        except Exception as e:
                            print(f"⚠️ 예외 발생: {school_type} | {payload} | 에러: {e}")
                            failed.append({"type": school_type, "payload": payload, "error": str(e)})

                        time.sleep(0.1)

    end = time.time()
    duration = round(end - start, 2)

    return {
        "message": f"{count}개 저장 완료",
        "type": type,
        "실패건수": len(failed),
        "소요시간(초)": duration,
        "실패리스트": failed[:3]  # 너무 많을 경우를 대비해 앞 3개만 예시로 반환
    }