import streamlit as st
import pandas as pd
import random
import datetime


def load_words_from_excel(file):
    """엑셀 파일에서 단어 리스트를 로드"""
    try:
        df = pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="cp949")  

    df.columns = df.columns.str.strip().str.lower()

    expected_cols = {'word', 'example', 'meaning'}
    actual_cols = set(df.columns)
    if not expected_cols.issubset(actual_cols):
        raise ValueError("엑셀 파일에 'word', 'example', 'meaning' 컬럼이 필요합니다.")

    words_list = []
    for _, row in df.iterrows():
        word_entry = {
            "word": str(row["word"]).strip(),
            "meaning": str(row["meaning"]).strip(),
            "example": str(row["example"]).strip()
        }
        words_list.append(word_entry)

    return words_list

def save_words_to_excel(dataset_name, words_list):
    import pandas as pd
    file_path = f"data/{dataset_name}.csv"
    df = pd.DataFrame(words_list)
    df.to_excel(file_path, index=False)


# ✅ 오늘의 단어 (임시 all_words)
all_words = [
    {"word": "abandon", "meaning": "버리다", "example": "He had to abandon his car in the storm."},
    {"word": "approach", "meaning": "접근하다", "example": "As we approached the city, the traffic increased."},
    {"word": "determine", "meaning": "결정하다", "example": "We need to determine the cause of the error."},
    {"word": "negotiation", "meaning": "협상", "example": "The negotiation between the two companies was successful."},
    {"word": "invoice", "meaning": "송장", "example": "Please attach the invoice to your payment confirmation."},
    {"word": "conference", "meaning": "회의", "example": "She will speak at an international education conference."},
    {"word": "alleviate", "meaning": "완화하다", "example": "The new policy is expected to alleviate traffic congestion."},
    {"word": "substantial", "meaning": "상당한", "example": "The company made a substantial investment in research."},
    {"word": "implication", "meaning": "영향", "example": "The decision will have serious implications for the economy."}
]

def get_today_words():
    """오늘의 단어: 날짜 기반 랜덤 5개"""
    today = datetime.date.today()
    random.seed(today.toordinal())
    return random.sample(all_words, 5)