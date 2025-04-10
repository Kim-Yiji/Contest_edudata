import pandas as pd
import pdfplumber
from konlpy.tag import Okt
from collections import Counter

# CSV 파일 로드
df = pd.read_csv('downloads/NewsResult_20250109-20250409.csv')

# 데이터의 첫 5줄 출력
print(df.head())

# PDF 파일 열기
with pdfplumber.open('세출예산 해설.pdf') as pdf:
    # 모든 페이지의 텍스트를 추출
    text = ''
    for page in pdf.pages:
        text += page.extract_text()

# KoNLPy의 Okt 형태소 분석기 초기화
okt = Okt()

# 텍스트에서 명사 추출
nouns = okt.nouns(text)

# 한 글자 단어 제거
nouns = [noun for noun in nouns if len(noun) > 1]

# 단어 빈도수 계산
word_freq = Counter(nouns)

# 가장 빈번한 단어 20개 출력
print("\n가장 빈번한 단어 20개:")
for word, freq in word_freq.most_common(20):
    print(f"{word}: {freq}") 