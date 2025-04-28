

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/report",
    tags=["report"]
)

class YearlyReportRequest(BaseModel):
    year: int

@router.post("/yearly")
def generate_yearly_report(request: YearlyReportRequest):
    """
    연별 뉴스 + 공공 데이터를 통합하여 보고서를 생성합니다.
    - year: 보고서 대상 연도 (예: 2025)
    """
    # TODO: 해당 연도 동안 수집된 뉴스 및 공공 데이터 종합 분석 및 보고서 생성 로직 추가
    # 예시) report_content = create_yearly_report(year=request.year)

    return {"message": f"Yearly report for {request.year} generation is triggered."}