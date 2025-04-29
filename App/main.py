from fastapi import FastAPI
<<<<<<< HEAD
# from App.news.news_router import router as news_router
# from App.publicdata.publicdata_router import router as publicdata_router
from App.news.news_collect_router import router as news_collect_router
from App.news.news_process_router import router as news_process_router
from App.news.news_result_router import router as news_result_router

from App.publicdata.publicdata_raw_router import router as publicdata_raw_router
from App.publicdata.publicdata_scoring_router import router as publicdata_scoring_router
from App.publicdata.publicdata_result_router import router as publicdata_result_router
from App.publicdata.publicdata_merge_router import router as publicdata_merge_router
from App.report.report_monthly import router as report_monthly_router
from App.report.report_yearly import router as report_yearly_router
from App.report.report_heatmap_router import router as report_heatmap_router
from App.report.report_priority_router import router as report_priority_router
from App.report.report_region_router import router as report_region_router
from App.report.report_table_router import router as report_table_router
from App.report.report_piechart_router import router as report_piechart_router
from App.gpt.gpt_summary_router import router as gpt_summary_router
=======
from App.news.news_router import router as news_router
from App.publicdata.publicdata_router import router as publicdata_router
from App.merge.merge_news_publicdata import router as merge_router
from App.report.report_monthly import router as report_monthly_router
from App.report.report_yearly import router as report_yearly_router
>>>>>>> a2c8b5abacb908656d06a6bead7187d4b67fbb56

app = FastAPI(
    title="학교 예결산서 월별/연별 보고서 API 서비스",
    description="학교의 회계 예결산서 데이터를 활용하여 월별 및 연별 보고서를 생성하는 API를 제공합니다.",
    version="1.0.0"
)

# 라우터 등록
<<<<<<< HEAD
# app.include_router(news_router)
# app.include_router(publicdata_router)
app.include_router(news_collect_router)
app.include_router(news_process_router)
app.include_router(news_result_router)
app.include_router(publicdata_raw_router)
app.include_router(publicdata_scoring_router)
app.include_router(publicdata_result_router)
app.include_router(report_monthly_router)
app.include_router(report_yearly_router)
app.include_router(publicdata_merge_router)
app.include_router(report_heatmap_router)
app.include_router(report_priority_router)
app.include_router(report_region_router)
app.include_router(report_table_router)
app.include_router(report_piechart_router)
app.include_router(gpt_summary_router)
=======
app.include_router(news_router)
app.include_router(publicdata_router)
app.include_router(merge_router)
app.include_router(report_monthly_router)
app.include_router(report_yearly_router)
>>>>>>> a2c8b5abacb908656d06a6bead7187d4b67fbb56

# 실행용 (uvicorn으로 실행할 때는 필요 없음)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("App.main:app", host="0.0.0.0", port=8000, reload=True)