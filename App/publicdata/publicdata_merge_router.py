

from fastapi import APIRouter

router = APIRouter(
    prefix="/publicdata",
    tags=["PublicData"]
)

@router.post("/result_generate")
def generate_publicdata_result():
    """
    공공 데이터 Scoring DB + 뉴스 예측 예산 활용 → 최종 예산 Result DB 저장
    """
    return {"message": "Public data result generated"}