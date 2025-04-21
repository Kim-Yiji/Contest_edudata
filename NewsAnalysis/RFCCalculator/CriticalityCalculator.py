import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import re
from tqdm import tqdm

# 정책 강도 키워드 사전 (LLM 기반)
POLICY_KEYWORDS = {
    # 긴급/위기/비상 상황
    "위기":        1.0,
    "긴급":        1.0,
    "비상":        1.0,
    "사태":        1.0,
    "폭발":        0.9,
    "전격":        0.9,
    "전면":        0.9,
    "강행":        0.9,
    # 제도·법령 변화
    "개정":        0.9,
    "폐지":        0.9,
    "추가":        0.8,
    "강화":        0.8,
    "신설":        0.8,
    "철회":        0.8,
    "입법":        0.8,
    "승인":        0.7,
    "거부":        0.7,
    "시행":        0.7,
    "시범":        0.6,
    "확대":        0.6,
    "축소":        0.6,
    "연기":        0.6,
    "유예":        0.6,
    # 예산·집행·분배
    "예산":        1.0,
    "추경":        0.9,
    "배정":        0.8,
    "집행":        0.8,
    "재정":        0.7,
    "투입":        0.7,
    "지원":        0.6,
    "교부":        0.6,
    # 감독·감시·평가
    "감사":        0.8,
    "국정감사":    0.8,
    "감독":        0.7,
    "모니터링":    0.6,
    "평가":        0.6,
    "성과":        0.6,
    "보고":        0.5,
    # 논의·토론·공청회
    "논의":        0.7,
    "토론":        0.7,
    "공청회":      0.7,
    "쟁점":        0.7,
    "의견수렴":    0.6,
    "포럼":        0.5,
    # 저항·반발·갈등
    "반발":        0.6,
    "항의":        0.6,
    "갈등":        0.6,
    "논란":        0.8,
    # 정보공개·발표·공표
    "발표":        0.5,
    "공표":        0.5,
    "공개":        0.5,
    "언론브리핑":  0.5,
    # 기타 이슈·키워드
    "파행":        0.9,
    "충격":        0.8,
    "심각":        0.8,
    "비판":        0.7,
    "우려":        0.6,
    "이행":        0.6,
    "제안":        0.5,
    "헌의":        0.5,
    "협의":        0.5,
    "협약":        0.5,
}

def get_keyword_score(text):
    """키워드 기반 정책 강도 점수 계산"""
    score = 0
    for keyword, weight in POLICY_KEYWORDS.items():
        if keyword in text:
            score += weight
    return min(score, 1.0)  # 최대 1.0으로 제한

def get_sentiment_score(text, tokenizer, model, device):
    """감성분석을 통해 긍정/부정 점수 계산"""
    # 텍스트가 None이거나 비어있는 경우 처리
    if text is None or not isinstance(text, str):
        text = str(text) if text is not None else ""
    
    # 텍스트가 비어있는 경우 중립 점수 반환
    if not text.strip():
        return 0.5
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1)
            
        # 긍정(1) 클래스의 확률을 감성 점수로 사용
        sentiment_score = probabilities[0][1].item()
        return sentiment_score
    except Exception as e:
        print(f"감성분석 중 오류 발생: {str(e)}")
        print(f"문제가 된 텍스트: {text}")
        return 0.5  # 오류 발생 시 중립 점수 반환

def calculate_criticality_score(news_text, sentiment_score, similarity_score):
    """Criticality 점수 계산 (키워드 + 감성 + 유사도)"""
    # 1. 키워드 기반 점수
    keyword_score = get_keyword_score(news_text)
    
    # 2. 감성 점수 변환 (긍정/부정에 따른 가중치)
    if sentiment_score < 0.3:  # 강한 부정
        sentiment_weight = 1.0
    elif sentiment_score < 0.5:  # 약한 부정
        sentiment_weight = 0.8
    elif sentiment_score > 0.7:  # 강한 긍정
        sentiment_weight = 0.6
    else:  # 중립
        sentiment_weight = 0.4
    
    # 3. 최종 Criticality 점수 계산
    criticality_score = (
        0.4 * keyword_score +  # 키워드 기반 점수
        0.3 * sentiment_weight +  # 감성 가중치
        0.3 * similarity_score  # 유사도 점수
    )
    
    return criticality_score, keyword_score, sentiment_weight

def calculate_and_save_criticality_scores(input_file):
    """Criticality 점수 계산 및 저장"""
    print("Criticality 점수 계산 중...")
    
    try:
        # 데이터 로드
        df = pd.read_csv(input_file)
        total_news = len(df)
        print(f"총 {total_news}개의 뉴스 데이터를 처리합니다.")
        
        # 데이터 유효성 검사
        if '제목' not in df.columns:
            raise ValueError("입력 파일에 '제목' 열이 없습니다.")
        if '유사도' not in df.columns:
            raise ValueError("입력 파일에 '유사도' 열이 없습니다.")
        
        print("감성분석 모델 로딩 중...")
        # 감성분석 모델 및 토크나이저 로드
        device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        print(f"사용 중인 방식: {'GPU 가속' if device.type == 'mps' else 'CPU'}")
        
        tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-FinBert-SC")
        model = AutoModelForSequenceClassification.from_pretrained("snunlp/KR-FinBert-SC").to(device)
        
        # Criticality 점수 계산
        criticality_scores = []
        print("\nCriticality 점수 계산 진행률:")
        for idx, row in tqdm(df.iterrows(), total=total_news, desc="진행률"):
            try:
                # 데이터 유효성 검사
                title = row['제목'] if pd.notna(row['제목']) else ""
                similarity_score = float(row['유사도']) if pd.notna(row['유사도']) else 0.0
                
                # 감성 점수 계산
                sentiment_score = get_sentiment_score(title, tokenizer, model, device)
                
                # Criticality 점수 계산
                criticality_score, keyword_score, sentiment_weight = calculate_criticality_score(
                    title, 
                    sentiment_score, 
                    similarity_score
                )
                
                criticality_scores.append({
                    '뉴스 식별자': row['뉴스 식별자'],
                    'criticality_score': criticality_score
                })
                
            except Exception as e:
                print(f"\n오류 발생 (인덱스: {idx})")
                print(f"제목: {row['제목']}")
                print(f"제목 타입: {type(row['제목'])}")
                print(f"제목 길이: {len(str(row['제목']))}자")
                print(f"유사도 점수: {row['유사도']}")
                print(f"유사도 점수 타입: {type(row['유사도'])}")
                print(f"오류 내용: {str(e)}")
                print(f"오류 유형: {type(e).__name__}")
                print("="*50)
                criticality_scores.append({
                    '뉴스 식별자': row['뉴스 식별자'],
                    'criticality_score': 0.0
                })
        
        # 결과를 DataFrame으로 변환
        result_df = pd.DataFrame(criticality_scores)
        
        # 출력 파일 경로 설정
        date_match = re.search(r'\d{8}-\d{8}', input_file)
        if date_match:
            date_str = date_match.group()
            output_file = os.path.join('NewsAnalysis/RFCData/C_score', f"CScore_{date_str}.csv")
        else:
            base_name = os.path.basename(input_file)
            output_file = os.path.join('NewsAnalysis/RFCData/C_score', f"CScore_{os.path.splitext(base_name)[0]}.csv")
        
        # 결과 저장
        print("\n결과 저장 중...")
        result_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"결과가 저장되었습니다: {output_file}")
        
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        print(f"오류 유형: {type(e).__name__}")
        print(f"오류가 발생한 파일: {input_file}")
        raise

def calculate_criticality_scores(df):
    """Criticality 점수 계산"""
    print("\nCriticality 점수 계산 중...")
    print(f"총 {len(df)}개의 뉴스 데이터를 처리합니다.")
    
    # 감성분석 모델 로딩
    print("감성분석 모델 로딩 중...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"사용 중인 방식: {'GPU 가속' if device == 'cuda' else 'CPU'}")
    model = AutoModelForSequenceClassification.from_pretrained("snunlp/KR-FinBert-SC")
    tokenizer = AutoTokenizer.from_pretrained("snunlp/KR-FinBert-SC")
    model.to(device)
    
    # 진행률 표시 설정
    total = len(df)
    print("\nCriticality 점수 계산 진행률:")
    progress_bar = tqdm(total=total, desc="진행률", unit="개")
    
    # 각 뉴스에 대해 Criticality 점수 계산
    criticality_scores = []
    for idx, row in df.iterrows():
        try:
            # 제목과 본문 결합
            text = f"{row['title']} {row['content']}"
            
            # 텍스트 전처리
            text = preprocess_text(text)
            
            # 텍스트가 비어있는 경우 처리
            if not text.strip():
                print(f"\n경고: 빈 텍스트 발견 (인덱스: {idx})")
                criticality_scores.append(0.0)
                progress_bar.update(1)
                continue
                
            # 토큰화 및 모델 입력
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # 감성분석 수행
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)
                negative_score = probabilities[0][0].item()
                positive_score = probabilities[0][1].item()
            
            # Criticality 점수 계산 (긍정 점수 - 부정 점수)
            score = positive_score - negative_score
            criticality_scores.append(score)
            
        except Exception as e:
            print(f"\n오류 발생 (인덱스: {idx})")
            print(f"제목: {row['title']}")
            print(f"본문 길이: {len(str(row['content']))}자")
            print(f"오류 내용: {str(e)}")
            print(f"오류 유형: {type(e).__name__}")
            print("="*50)
            criticality_scores.append(0.0)
            
        progress_bar.update(1)
    
    progress_bar.close()
    return criticality_scores

if __name__ == "__main__":
    input_file = input("Criticality 점수를 계산할 파일 경로를 입력하세요: ")
    if not os.path.exists(input_file):
        print(f"오류: 입력 파일이 존재하지 않습니다: {input_file}")
        exit(1)
    
    calculate_and_save_criticality_scores(input_file) 