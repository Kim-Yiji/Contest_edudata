from fastapi import APIRouter

router = APIRouter(
    prefix="/news",
    tags=["News"]
)

@router.post("/collect")
def collect_news():
    return {"message": "News collection endpoint"}
