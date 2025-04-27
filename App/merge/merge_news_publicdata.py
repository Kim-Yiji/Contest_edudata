from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/merge",
    tags=["merge"]
)

class MergeRequest(BaseModel):
    news_finished: int
    public_finished: int

@router.post("/news_and_publicdata")
def merge_news_and_publicdata_status_check(request: MergeRequest):
    """
    뉴스 데이터와 공공 데이터가 모두 처리 완료되었는지 확인 후 병합을 수행합니다.
    - news_finished: 뉴스 데이터 처리 완료 여부 (1: 완료, 0: 미완료)
    - public_finished: 공공 데이터 처리 완료 여부 (1: 완료, 0: 미완료)
    """
    if request.news_finished != 1 or request.public_finished != 1:
        raise HTTPException(status_code=400, detail="News or Publicdata processing not finished.")

    # TODO: 실제 뉴스 데이터와 공공 데이터 병합 로직 추가
    # 예시) merged_data = merge_function(news_data, public_data)

    return {"message": "Merging news and public data is successfully triggered."}