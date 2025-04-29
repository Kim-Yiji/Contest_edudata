from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/report",
    tags=["Report"]
)

class MonthlyReportRequest(BaseModel):
    year: int
    month: int

@router.post("/monthly")
def generate_monthly_report(request: MonthlyReportRequest):
    """
    월별 뉴스 데이터를 기반으로 보고서를 생성합니다.
    - year: 보고서 대상 연도 (예: 2025)
    - month: 보고서 대상 월 (예: 4)
    """
    # TODO: 해당 연도/월의 뉴스 데이터를 조회하여 보고서 생성 로직 추가
    # 예시) report_content = create_monthly_report(year=request.year, month=request.month)

    return {"message": f"Monthly report for {request.year}-{request.month:02d} generation is triggered."}
