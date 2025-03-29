from fastapi import FastAPI
from App.schoolinfo.public_schoolinfo_router import router as schoolinfo_router
from App.schoolinfo.private_schoolinfo_router import router as private_school_router
from App.schoolinfo.schoolinfo_batch_router import router as batch_router


app = FastAPI(
    title="학교알리미 데이터 API 서비스",
    description="학교 회계 예·결산서 등의 정보를 학교알리미 API를 통해 제공합니다.",
    version="1.0.0"
)

# 라우터 등록
app.include_router(schoolinfo_router)
app.include_router(private_school_router)
app.include_router(batch_router)

# 실행용 (uvicorn으로 실행할 때는 필요 없음)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("App.main:app", host="0.0.0.0", port=8000, reload=True)