import streamlit as st
from sidebar import show_sidebar
from main import run_main
from wordbook_high import run_wordbook_high
from wordbook_toeic import run_wordbook_toeic
from wordbook_teps import run_wordbook_teps
from todays_word import run_today_words
from test import run_test
from result_rank import run_result_rank
from db import init_db, init_user_stats

# 초기화
init_db()
init_user_stats()

# 페이지 설정
st.set_page_config(page_title="Your vocab", layout="centered")

# 사이드바 표시
show_sidebar()

# 페이지 라우팅
page = st.session_state.get("page", "intro")

if page == "main":
    run_main()
elif page == "wordbook_high":
    run_wordbook_high()
elif page == "wordbook_toeic":
    run_wordbook_toeic()
elif page == "wordbook_teps":
    run_wordbook_teps()
elif page == "test":
    run_test()
elif page == "result":
    run_result_rank()
elif page == "todays_word":
    run_today_words()
else:
    # 인트로 화면
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
            .content-text {
                font-size: 17px;
                color: #444;
                line-height: 1.8;
                text-align: center;
            }
            .footer {
                font-size: 14px;
                color: #aaa;
                margin-top: 60px;
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>Your Vocab</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>대학생을 위한 영어 단어 학습 프로그램</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='content-text'>
    대학생들이 TOEIC, TEPS, 수능과 같은 영어 시험을 준비하는 과정에서<br/>
    단어 암기 효율을 높이기 위한 학습 도구를 개발하는 것을 목표로 합니다.<br/><br/>
    단순 암기식 학습의 한계를 보완하기 위해 테스트 기능, 영어 학습 횟수를 이용한 랭킹 기능,<br/>
    단어 로테이션 등 다양한 학습 방식을 제공합니다.<br/><br/>
    이런 기능들을 바탕으로 사용자가 반복적으로 학습하고<br/>
    자신의 실력을 확인할 수 있도록 설계된 웹 기반 영어 단어 학습 프로그램입니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='footer'>&copy; 2025 Your Vocab. All rights reserved.</div>", unsafe_allow_html=True)