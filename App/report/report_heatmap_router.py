

from fastapi import APIRouter

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

@router.post("/heatmap_generate")
def generate_heatmap():
    """
    공공 데이터 Result DB 기반 지도 히트맵 생성 API
    """
    return {"message": "Heatmap successfully generated"}