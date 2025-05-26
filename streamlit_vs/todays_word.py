import streamlit as st
from word_data import get_today_words  # 이미 만든 함수에서 20개 단어 불러오기
import requests
from word_data import load_words_from_excel
from admin import show_admin_panel
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd

# 여기서부터는 추가된 20개 오늘의 단어입니다

# 웹페이지 URL
url = "https://englishparadise.tistory.com/61"

# 웹페이지 요청
response = requests.get(url)
response.raise_for_status()  # 요청이 성공했는지 확인

# HTML 파싱
soup = BeautifulSoup(response.text, "html.parser")

# 본문 내용 추출
content_div = soup.find("div", class_="tt_article_useless_p_margin")
if not content_div:
    raise ValueError("본문 내용을 찾을 수 없습니다.")

# 텍스트 추출 및 전처리
text = content_div.get_text(separator="\n")
text = text.replace("\xa0", " ").strip()

# 불필요한 서두 제거
start_phrase = "영단어 정리"
start_index = text.find(start_phrase)
if start_index == -1:
    raise ValueError("영단어 정리 부분을 찾을 수 없습니다.")
text = text[start_index + len(start_phrase):].strip()

# 단어와 의미 분리
lines = text.split("\n")
word_meanings = []
for line in lines:
    if " - " in line:
        word, meaning = line.split(" - ", 1)
        word_meanings.append((word.strip(), meaning.strip()))

with open("today_words20.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["word", "meaning"])
    for word, meaning in word_meanings:
        writer.writerow([word, meaning])



def run_today_words():
    
    if "today_words" not in st.session_state:
        try:
            words = get_today_words()
            if not words or len(words) == 0:
                st.error("오늘의 단어가 준비되지 않았습니다.")
                return
            st.session_state.today_words = words
        except Exception as e:
            st.error("오늘의 단어가 준비되지 않았습니다.")
            return
    
    words = st.session_state.today_words
    
    # 인덱스 초기화
    if "today_index" not in st.session_state:
        st.session_state.today_index = 0

    # 현재 단어 가져오기
    idx = st.session_state.today_index
    current = words[idx]

    # 스타일
    st.markdown(f"""
        <h2 style='margin-bottom: 10px;'>📅 Today’s Word</h2>
        <div style='padding: 20px; background-color: #f3f3f3; border-radius: 10px; text-align: center;'>
            <h1 style='font-size: 36px; color: #4CAF50;'>{current['word']}</h1>
            <p style='font-size: 20px; color: #333;'><b>뜻:</b> {current['meaning']}</p>
            <p style='font-style: italic; color: #666;'>{current['example']}</p>
        </div>
    """, unsafe_allow_html=True)


    # 네비게이션 버튼
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("⬅", key="prev_word"):
            st.session_state.today_index = (idx - 1) % len(words)
            st.rerun()
    with col3:
        if st.button("➡", key="next_word"):
            st.session_state.today_index = (idx + 1) % len(words)
            st.rerun()

    st.caption(f"{idx + 1} / {len(words)}")


    st.markdown("---")

    if st.button("📝 Today's test"):
        st.session_state.test_type = "today"
        st.session_state.questions = st.session_state.today_words
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.correct = 0
        st.session_state.wrong = 0
        st.session_state.wrong_words = []
        st.session_state.page = "test"
        st.session_state.show_ranking = True
        st.rerun()

    # "+ more" 확장 영역 추가
    with st.expander("+ more"):
        try:
            # CSV 파일 불러오기
            df = pd.read_csv("today_words20.csv")

            # 무작위로 20개 선택
            df_sampled = df.sample(n=20, random_state=None).reset_index(drop=True)

            # 번호 붙이기
            df_sampled.index = range(1, 21)
            df_sampled.index.name = "No."

            # 표 출력
            st.dataframe(df_sampled, use_container_width=True)

        except FileNotFoundError:
            st.error("❌ today_words20.csv 파일을 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")