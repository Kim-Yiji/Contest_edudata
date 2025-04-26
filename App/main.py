from fastapi import FastAPI
from App.publicdata.schoolinfo.public_schoolinfo_router import router as schoolinfo_router
from App.publicdata.schoolinfo.private_schoolinfo_router import router as private_school_router
from App.publicdata.schoolinfo.schoolinfo_batch_router import router as batch_router
from App.news.news_router import router as news_router
from App.publicdata.publicdata_router import router as publicdata_router

app = FastAPI(
    title="학교 예결산서 월별/연별 보고서 API 서비스",
    description="학교의 회계 예결산서 데이터를 활용하여 월별 및 연별 보고서를 생성하는 API를 제공합니다.",
    version="1.0.0"
)

# 라우터 등록
app.include_router(schoolinfo_router)
app.include_router(private_school_router)
app.include_router(batch_router)
app.include_router(news_router)
app.include_router(publicdata_router)

# 실행용 (uvicorn으로 실행할 때는 필요 없음)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("App.main:app", host="0.0.0.0", port=8000, reload=True)