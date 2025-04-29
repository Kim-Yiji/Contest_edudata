

from fastapi import APIRouter

router = APIRouter(
    prefix="/news",
    tags=["News"]
)

@router.post("/top10/tabledata")
def get_top10_tabledata():
    return {"message": "Top 10 news table data endpoint"}

@router.post("/keywords/wordcloud")
def get_keywords_wordcloud():
    return {"message": "Keywords word cloud endpoint"}

@router.post("/top_category_3")
def get_top3_categories():
    return {"message": "Top 3 news categories endpoint"}