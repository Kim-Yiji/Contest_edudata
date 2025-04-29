from fastapi import APIRouter

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

@router.post("/region_summation")
def generate_region_summation():
    """
    공공 데이터 Result DB 기반 지역별 예산 Summation API
    """
    return {"message": "Region summation successfully generated"}
