from fastapi import APIRouter

router = APIRouter(
    prefix="/news",
    tags=["News"]
)

@router.post("/process_monthly")
def process_news_monthly():
    return {"message": "News monthly processing endpoint"}

@router.post("/process_yearly")
def process_news_yearly():
    return {"message": "News yearly processing endpoint"}
