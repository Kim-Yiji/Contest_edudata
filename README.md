# Contest_edudata
25-1 교육 공공데이터 공모전

1. uvicorn App.main:app --reload
2. http://localhost:8000/docs
3. certifi 관련 환경 셋업 - 난 그냥 verify = False 해버림
4-1. API/schoolinfo/schoolinfo_batch.py
4-2. curl -X POST "http://localhost:8000/schoolinfo/batch?type=both"  : type에서 private, public 선택가능