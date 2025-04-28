import requests

def fetch_budget_data(api_key: str, api_type: str, pbanYr: int, schulKndCode: str, depthNo: str, depthNo2: str) -> dict:
    url = "http://www.schoolinfo.go.kr/openApi.do"
    params = {
        "apiKey": api_key,
        "apiType": api_type,
        "pbanYr": pbanYr,
        "schulKndCode": schulKndCode,
        "depthNo": depthNo,
        "depthNo2": depthNo2
    }

    response = requests.get(url, params=params, verify=False)
    if response.status_code != 200:
        raise Exception(f"API 요청 실패: {response.status_code}, {response.text}")
    
    data = response.json()

    if "RESULT" in data:
        raise Exception(f"데이터 없음 또는 API 오류: {data['RESULT']}")

    return data