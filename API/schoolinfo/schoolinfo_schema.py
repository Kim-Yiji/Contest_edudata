from pydantic import BaseModel

class SchoolBudgetRequest(BaseModel):
    pbanYr: int          # 연도
    schulKndCode: str    # 학교급구분
    depthNo: str         # 예산/결산
    depthNo2: str        # 세입/세출