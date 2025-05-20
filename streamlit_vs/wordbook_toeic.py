import streamlit as st
from word_data import load_words_from_excel
from admin import show_admin_panel

import requests
from bs4 import BeautifulSoup

def get_toeic():
    url = "https://www.lable.co.kr/%ED%86%A0%EC%9D%B5_%EC%96%B4%ED%9C%98_%EC%9E%90%EB%A3%8C/1518809"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'

    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    paragraphs = soup.find_all('p')
    
    results = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            results.append(text)
    
    return results

import re

def trans_toeic_data(text_lines):
    parsed = []
    drop_words = {"resume", "trust", "category", "rapport", "moment"}
    pattern = r"^\(\d+\)\s*(.+?)\s*:\s*(.+)"
    
    i = 0
    while i < len(text_lines):
        match = re.match(pattern, text_lines[i])
        if match:
            word = match.group(1).strip()
            meaning = match.group(2).strip()
            
            if i + 2 < len(text_lines):
                example = text_lines[i + 1].strip()
                example_meaning = text_lines[i + 2].strip()

                if word.lower() in drop_words:
                    i += 3
                    continue

                parsed.append({
                    "word": word,
                    "meaning": meaning,
                    "example": example,
                    "example_meaning": example_meaning
                })
                i += 3
            else:
                i += 1
        else:
            i += 1
    
    return parsed

raw_lines = get_toeic()
toeic_dicts = trans_toeic_data(raw_lines)

import re

def get_word_variants(word):
    return [
        word,                     
        word + "s",              
        word + "ed",             
        word + "ing",            
        word + "es",             
        word + "d" if word.endswith('e') else "", 
    ]

for entry in toeic_dicts:
    word = entry["word"]
    example = entry["example"]

    variants = get_word_variants(word)
    variants = [v for v in variants if v]

    pattern = r'\b(' + '|'.join(map(re.escape, variants)) + r')\b'

    replaced_example = re.sub(pattern, '_________', example, flags=re.IGNORECASE)

    entry["example"] = replaced_example

import csv

with open("toeic.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["word", "meaning", "example", "example_meaning"])
    writer.writeheader()
    for entry in toeic_dicts:
        writer.writerow(entry)


def run_wordbook_toeic():
    # ✅ 토익 단어장 파일 경로
    FILE_PATH = "toeic.csv"

    # ✅ session_state에 단어장 초기화 + 예외 흐름 추가
    try:
        if "wordbook" not in st.session_state:
            st.session_state.wordbook = load_words_from_excel(FILE_PATH)
            if not st.session_state.wordbook:  
                st.error("단어 목록을 불러올 수 없습니다.")
                return
    except Exception as e:
        st.error("단어 목록을 불러올 수 없습니다.")
        return
    
    if "keep_words" not in st.session_state:
        st.session_state.keep_words = []

    st.title("📕TOEIC")

    # ✅ 관리자 모드
    if st.session_state.get("role") == "admin":
        st.session_state.dataset = "toeic"
        show_admin_panel()

    # ✅ 시험으로 이동 버튼
    if st.button("📝 taking a test", key="to_test_wordbook"):
        st.session_state["test_type"] = "toeic"
        st.session_state.page = "test"
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.correct = 0
        st.session_state.wrong = 0
        st.session_state.wrong_words = []
        st.session_state.show_ranking = False
        st.rerun()

    # ✅ 탭 나누기
    tab1, tab2 = st.tabs(["📖 Wordbook", "📌"])

    with tab1:
        st.subheader("전체 단어")
        for item in st.session_state.wordbook:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['word']}** - {item['meaning']}")
            with col2:
                if st.button("📌 Keep", key=f"keep_{item['word']}"):
                    try:
                        if item in st.session_state.keep_words:
                            st.info("이미 저장된 단어입니다.")
                        else:
                            st.session_state.keep_words.append(item)
                            st.success("저장 완료.")
                    except Exception as e:
                        st.error("저장 실패.")
                


    with tab2:
        st.subheader("❗ 저장한 단어 (Keep)")
        if not st.session_state.keep_words:
            st.info("아직 저장한 단어가 없습니다.")
        else:
            for i, item in enumerate(st.session_state.keep_words):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{item['word']}** - {item['meaning']}")
                with col2:
                    if st.button("🗑️ 삭제", key=f"remove_{i}"):
                        st.session_state.keep_words.pop(i)
                        st.rerun()
