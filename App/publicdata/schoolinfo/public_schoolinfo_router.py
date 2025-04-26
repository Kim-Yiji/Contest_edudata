from fastapi import APIRouter, HTTPException
from API.schoolinfo.schoolinfo import fetch_budget_data
from API.schoolinfo.schoolinfo_schema import SchoolBudgetRequest
from App.config import API_KEY
from utils.data_handler import save_json
import traceback

router = APIRouter(prefix="/publicschool", tags=["SchoolInfo"])

@router.post("/budget")
def get_budget_and_save(request: SchoolBudgetRequest):
    try:
        # 1. 외부 API 호출
        data = fetch_budget_data(
            api_key=API_KEY,
            api_type="27",
            pbanYr=request.pbanYr,
            schulKndCode=request.schulKndCode,
            depthNo=request.depthNo,
            depthNo2=request.depthNo2
        )

        # 2. 파일 이름 만들기
        kind_map = {"02": "초등", "03": "중등", "04": "고등", "05": "특수", "06": "기타", "07": "각종"}
        depth1_map = {"10": "예산", "20": "결산"}
        depth2_map = {"1": "세입", "2": "세출", "3": "세입", "4": "세출"}

        name = f"공립_{kind_map.get(request.schulKndCode, '기타')}_{depth1_map[request.depthNo]}_{depth2_map[request.depthNo2]}_{request.pbanYr}.json"

        # 3. 저장
        save_json(data, folder="Database/schoolinfo/public", filename=name)

        return {"message": "데이터 저장 완료", "filename": name, "data_preview": data[:1] if isinstance(data, list) else "JSON"}

    except Exception as e:
        # traceback.print_exc()  # 서버 터미널에 에러 로그 전체 출력
        raise HTTPException(status_code=500, detail=f"외부 API 요청 실패: {str(e)}")