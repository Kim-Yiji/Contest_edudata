# Contest_edudata
25-1 교육 공공데이터 공모전

## 프로젝트 개요
- 학교 예결산서 및 뉴스 데이터를 활용하여 월별, 연별 교육 관련 보고서를 생성하는 시스템입니다.
- 공공데이터 (학교 예결산 데이터)와 뉴스 데이터를 기반으로 분석 및 자동화 보고서 작성을 지원합니다.

## 실행 방법

0. config 파일 세팅  
   - `App/publicdata/schoolinfo/config.py` 파일에 `API_KEY = "발급된 키"` 형태로 작성합니다.

1. FastAPI 서버 실행  
   ```bash
   PYTHONPATH=. uvicorn App.main:app --reload
   ```

2. Swagger 문서 접속 (API 테스트 가능)  
   - [http://localhost:8000/docs](http://localhost:8000/docs)

3. SSL 인증서 관련 오류 발생 시  
   - requests 모듈 사용 시 `verify=False` 옵션 추가로 회피

## 주요 API 구조

### 퍼블릭 데이터 (학교 예결산서 관련)
- `/publicdata/schoolinfo/publicschool/budget` : 공립학교 예산 데이터 수집
- `/publicdata/schoolinfo/privateschool/budget` : 사립학교 예산 데이터 수집
- `/publicdata/schoolinfo/batch` : 공공데이터(공립/사립) 일괄 수집

> 호출 예시:  
> ```bash
> curl -X POST "http://localhost:8000/publicdata/schoolinfo/batch?type=both"
> ```

### 뉴스 데이터
- `/news/process_monthly` : 월별 뉴스 데이터 분석 및 저장
- `/news/process_yearly` (예정) : 연별 뉴스 데이터 분석

## 기타 유틸리티
- 교육청 데이터 필터링 예시:
  ```bash
  python utils/get_gyeonggi.py
  ```

---

## 정리
- 월별: 뉴스 데이터를 분석하여 월간 교육 여론 트렌드 보고서 생성
- 연별: 뉴스 + 공공데이터를 통합 분석하여 연간 교육 예결산 평가 보고서 생성