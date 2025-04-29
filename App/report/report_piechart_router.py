from fastapi import APIRouter

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

@router.post("/final_piecharts")
def generate_final_piecharts():
    """
    예산 DB + 뉴스 예측 예산 기반 파이 차트 생성 API
    """
    return {"message": "Final pie charts successfully generated"}
