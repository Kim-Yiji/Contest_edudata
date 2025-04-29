from fastapi import APIRouter

router = APIRouter(
    prefix="/gpt",
    tags=["GPT"]
)

@router.post("/summary_generation")
def generate_gpt_summary():
    """
    GPT API를 이용한 해설/요약 문장 생성 API
    """
    return {"message": "GPT-based summary successfully generated"}
