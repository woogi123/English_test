import streamlit as st
import requests
from bs4 import BeautifulSoup
from wordbook_high import run_wordbook_high
from wordbook_toeic import run_wordbook_toeic
from wordbook_teps import run_wordbook_teps

def run_main():

    # 오늘의 단어 크롤링 함수
    @st.cache_data(show_spinner=False)
    def get_today_word():
        try:
            url = "https://en.dict.naver.com/#/main"
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            # 예시 걍 아무거나 넣었음
            return {"word": "diligent", "meaning": "성실한", "example": "She is a diligent student."}
        except:
            return {"word": "diligent", "meaning": "성실한", "example": "She is a diligent student."} 

    # 오늘의 단어 정보
    today = get_today_word()
                
    # 메인 콘텐츠
    st.markdown("<div class='title'>Your Vocab</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Choose your learning mode</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📗 수능")
        st.write("기본 영단어 학습")
        if st.button("수능 vocab"):
            st.session_state.page = "wordbook_high"
            st.rerun()
    with col2:
        st.markdown("### 📕 TOEIC")
        st.write("비즈니스 중심 영어")
        if st.button("TOEIC voab"):
            st.session_state.page = "wordbook_toeic"
            st.rerun()

    with col3:
        st.markdown("### 📘 TEPS")
        st.write("고급 독해 어휘")
        if st.button("TEPS vocab"):
            st.session_state.page = "wordbook_teps"
            st.rerun()

    st.markdown("---")

    # 오늘의 단어 카드
    st.markdown("## 📅 Today's word")
    st.markdown(f"### `{today['word']}` — {today['meaning']}")
    st.markdown(f"> _{today['example']}_")
    if st.button("→ 오늘의 단어 보기"):
        st.session_state.page = "todays_word"
        st.rerun()

    # 스타일 설정
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            html, body, [class*="css"]  {
                font-family: 'Inter', sans-serif;
            }
            .title {
                font-size: 42px;
                font-weight: 600;
                margin-bottom: 10px;
                line-height: 1.3;
                text-align: center;
            }
            .subtitle {
                font-size: 20px;
                font-weight: 400;
                color: #666;
                text-align: center;
                margin-bottom: 30px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='footer'>&copy; 2025 Your Vocab. All rights reserved.</div>", unsafe_allow_html=True)
