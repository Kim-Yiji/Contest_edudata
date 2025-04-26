from fastapi import APIRouter

router = APIRouter(
    prefix="/news",
    tags=["News"],
)

@router.post("/collect", summary="Collect News Data")
async def collect_news_data():
    # 여기에 실제 크롤링하거나 데이터 가져오는 로직 연결
    return {"message": "News data collected"}

@router.post("/process_monthly", summary="Process Monthly News")
async def process_monthly_news():
    return {"message": "Monthly news processed"}

@router.post("/process_yearly", summary="Process Yearly News")
async def process_yearly_news():
    return {"message": "Yearly news processed"}