from fastapi import APIRouter, HTTPException
from API.publicdata.schoolinfo.schoolinfo import fetch_budget_data
from API.publicdata.schoolinfo.schoolinfo_schema import SchoolBudgetRequest
from App.publicdata.schoolinfo.config import API_KEY
from utils.data_handler import save_json

router = APIRouter(prefix="/publicdata/schoolinfo", tags=["Public Data"])

@router.post("/private/budget", summary="Get Private School Budget and Save")
def get_private_budget(request: SchoolBudgetRequest):
    try:
        data = fetch_budget_data(
            api_key=API_KEY,
            api_type="28",  # 사립학교용
            pbanYr=request.pbanYr,
            schulKndCode=request.schulKndCode,
            depthNo=request.depthNo,
            depthNo2=request.depthNo2
        )

        kind_map = {"02": "초등", "03": "중등", "04": "고등", "05": "특수", "06": "기타", "07": "각종"}
        depth1_map = {"10": "예산", "20": "결산"}
        depth2_map = {"1": "세입", "2": "세출", "3": "세입", "4": "세출"}

        filename = f"사립_{kind_map.get(request.schulKndCode, '기타')}_{depth1_map[request.depthNo]}_{depth2_map[request.depthNo2]}_{request.pbanYr}.json"

        save_json(data, folder="Database/schoolinfo/private", filename=filename)

        return {"message": "사립학교 데이터 저장 완료", "filename": filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))