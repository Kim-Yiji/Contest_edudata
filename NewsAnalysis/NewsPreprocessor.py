import pandas as pd
import re
from tqdm import tqdm
import os

# 뉴스필터링 키워드 (LLM 기반).py에서 키워드 가져오기
INCLUDE_KEYWORDS = [
    # 메인 키워드
    "초등", "중등", "고등", "초중고", "초등학교", "중학교", "고등학교",
    "교실", "학급", "담임", "교사", "스쿨존", "하교", "등교",
    "학부모", "교장", "교감", "학교급식", "학교폭력", "교내",
    # 추가 키워드 — 일반/정책
    "교육청", "교육부", "교육감", "교육정책", "교육재정",
    "교육과정", "교과과정", "교재", "교과서",
    # 학생·학습·평가
    "학생", "학생상담", "학생생활", "학습", "기초학력", "학업성취도",
    "평가", "교육평가", "내신", "수능", "대입", "입시",
    # 수업·교실 혁신
    "수업", "원격수업", "온라인수업", "스마트교실", "에듀테크",
    "디지털교과서", "코딩교육", "SW교육", "ICT교육",
    # 유아·돌봄·방과후
    "유치원", "어린이집", "누리과정", "돌봄교실", "방과후학교",
    "돌봄서비스", "방학", "학기", "방학중교실",
    # 복지·지원·장학
    "교육복지", "무상교육", "무상급식", "교육급여",
    "장학금", "학비지원", "학생복지", "교육지원",
    # 특수·통합·다문화
    "특수교육", "장애학생", "통합교육", "다문화", "다문화교육",
    # 연구·혁신학교
    "혁신학교", "연구학교", "선도학교",
    # 시설·환경·안전
    "교육환경", "시설개선", "노후교실", "교실환경", "그린스마트스쿨",
    "체육관", "음악실", "미술실", "급식재료", "학교시설",
    "학교안전", "안전교육", "통학버스", "교통안전",
    # 보건·건강
    "보건실", "건강검진", "응급처치", "감염병", "코로나", "독감", "예방접종",
    # 학원·사교육
    "학원", "사교육",
    # 영재·창의
    "영재교육", "창의교육",
    # 기타 교육 키워드
    "교원", "교원연수", "교원채용", "교원수급", "교원충원",
    "교내활동", "교외활동", "학교행정", "교무학사", "학교운영"
]

EXCLUDE_KEYWORDS = [
    # ── 정치/수사 이슈
    "소환조사", "압수수색", "기소", "구속영장", "공소시효",
    "특활비", "청탁금지법", "검찰조사", "위증", "직권남용",
    "정계개편", "공천", "총선", "대선", "청문회", "보궐선거",
    "야당", "여당", "당대표",

    # ── 도시/건설/교통 개발
    "도로확장", "재건축", "지하차도", "아파트분양",
    "산업단지", "택지개발", "건설수주", "용적률", "역세권개발",
    "교통정비",

    # ── 연예·방송·문화 단신
    "연예인", "아이돌", "드라마", "뮤직비디오", "콘서트",
    "팬미팅", "티저공개", "예능", "앨범발매",

    # ── 외교·국방·경제 이슈
    "북핵", "군사훈련", "국방부", "무역적자", "환율",
    "금리인상", "반도체수출", "기준금리", "유가", "외환보유액",

    # ── 비(非)교육 복지/사회 정책
    "기초생활수급", "긴급복지", "생계급여", "간병서비스",
    "노인복지관", "돌봄로봇", "활동보조", "주거급여",
    "요양보호사", "기초연금", "노인일자리", "평생교육",

    # ── 청년·주거 정책
    "청년월세지원", "전세대출", "공공임대", "청년정책",
    "신혼희망타운", "LH청약", "청년취업지원금", "청년창업센터",

    # ── 보건·재난 대응 (교육 맥락 외)
    "백신접종", "병상확보", "의료진지원", "코로나입원",
    "환자이송", "중환자병상", "응급의료법", "의사협회",
    "방역인력",

    # ── 노조·노동·산업 이슈
    "임단협", "노조파업", "근로시간단축", "고용유지지원금",
    "노사정협의", "단체협약", "공공기관채용", "산업인력공단",

    # ── 치안·안전 단신
    "뺑소니", "보복운전", "치안유지", "경찰수사",

    # ── 기타 주제
    "종교행사", "성지순례", "스포츠단신", "은퇴발표",
    "골프우승", "국가대표선발", "개인사", "가족사"
]

def clean_text(text):
    """텍스트 정제 함수"""
    if pd.isna(text):
        return ""
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수문자 제거 (한글, 영문, 숫자, 공백만 남김)
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    
    # 연속된 공백을 하나로 통일
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def contains_any_keyword(text, keywords):
    """주어진 텍스트에 키워드 목록 중 하나 이상이 포함되어 있는지 확인"""
    return any(keyword in text for keyword in keywords)

def preprocess_news_data(input_file, output_file):
    """뉴스 데이터 전처리 함수"""
    print("뉴스 데이터 로딩 중...")
    df = pd.read_csv(input_file, encoding='utf-8')
    initial_count = len(df)
    print(f"초기 데이터 개수: {initial_count:,}개")
    
    print("\n불필요한 열 제거 중...")
    # 제거할 열 목록
    columns_to_drop = [
        '기고자', '통합 분류1', '통합 분류2', '통합 분류3',
        '사건/사고 분류1', '사건/사고 분류2', '사건/사고 분류3',
        '인물', '위치', '기관', '본문', '분석제외 여부'
    ]
    
    # 존재하는 열만 제거
    existing_columns = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=existing_columns)
    print(f"제거된 열: {', '.join(existing_columns)}")
    
    print("\n데이터 전처리 중...")
    # 텍스트 정제
    df['제목'] = df['제목'].apply(clean_text)
    df['특성추출(가중치순 상위 50개)'] = df['특성추출(가중치순 상위 50개)'].apply(clean_text)
    
    # 1단계: 포함 키워드 필터링
    print("\n포함 키워드 필터링 중...")
    include_filter = df.apply(lambda row: contains_any_keyword(row['제목'] + ' ' + row['특성추출(가중치순 상위 50개)'], INCLUDE_KEYWORDS), axis=1)
    included_news = df[include_filter]
    print(f"포함 키워드로 필터링된 기사: {len(included_news):,}개")
    
    # 2단계: 제외 키워드 필터링
    print("\n제외 키워드 필터링 중...")
    exclude_filter = included_news.apply(lambda row: not contains_any_keyword(row['제목'] + ' ' + row['특성추출(가중치순 상위 50개)'], EXCLUDE_KEYWORDS), axis=1)
    final_df = included_news[exclude_filter]
    print(f"제외 키워드로 필터링된 후 남은 기사: {len(final_df):,}개")
    
    # 중복 기사 제거 (제목 기준)
    print("\n중복 기사 제거 중...")
    duplicate_count = final_df.duplicated(subset=['제목']).sum()
    final_df = final_df.drop_duplicates(subset=['제목'], keep='first')
    print(f"제거된 중복 기사: {duplicate_count:,}개")
    print(f"최종 남은 기사: {len(final_df):,}개")
    
    # 결과 저장
    print("\n결과 저장 중...")
    final_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print("\n=== 전처리 결과 요약 ===")
    print(f"초기 데이터 개수: {initial_count:,}개")
    print(f"포함 키워드로 필터링된 기사: {len(included_news):,}개")
    print(f"제외 키워드로 필터링된 후 남은 기사: {len(final_df):,}개")
    print(f"제거된 중복 기사: {duplicate_count:,}개")
    print(f"최종 남은 기사: {len(final_df):,}개")
    
    return final_df

if __name__ == "__main__":
    # 사용자 입력 받기
    input_file = input("전처리할 데이터의 파일 경로를 입력하세요 (예: NewsAnalysis/NewsData/Raw/20250312-20250412.csv): ")
    
    # 입력 파일 존재 여부 확인
    if not os.path.exists(input_file):
        print(f"오류: 입력 파일이 존재하지 않습니다: {input_file}")
        exit(1)
    
    # 출력 디렉토리 설정
    preprocessed_dir = "NewsAnalysis/NewsData/Preprocessed"
    os.makedirs(preprocessed_dir, exist_ok=True)
    
    # 입력 파일명에서 날짜 추출
    date_match = re.search(r'\d{8}-\d{8}', input_file)
    if date_match:
        date_str = date_match.group()
        output_file = os.path.join(preprocessed_dir, f"Preprocessed_{date_str}.csv")
    else:
        # 날짜가 없는 경우 원본 파일명 사용
        base_name = os.path.basename(input_file)
        output_file = os.path.join(preprocessed_dir, f"Preprocessed_{base_name}")
    
    print(f"\n입력 파일: {input_file}")
    print(f"출력 파일: {output_file}")
    
    preprocess_news_data(input_file, output_file) 