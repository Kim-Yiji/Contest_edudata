

from fastapi import APIRouter

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

@router.post("/priority_summary")
def generate_priority_summary():
    """
    공공 데이터 Result DB 기반 지역별 우선순위 요약 생성 API
    """
    return {"message": "Priority summary successfully generated"}