

from fastapi import APIRouter

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

@router.post("/final_table_generate")
def generate_final_table():
    """
    예산 DB + 뉴스 예측 예산 기반 표 데이터 생성 API
    """
    return {"message": "Final table data successfully generated"}