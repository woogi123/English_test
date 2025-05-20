import streamlit as st
import sqlite3
import random
from word_data import load_words_from_excel, get_today_words
from db import init_db, register_user, login_user, get_all_users, delete_user_by_email

init_db()

def show_sidebar():

    # 엑셀 파일 경로 정의
    SUNEUNG_FILE = "suneung.csv"
    TOEIC_FILE = "toeic.csv"
    TEPS_FILE = "teps.csv"

# 로그인 팝업
    @st.dialog("🔐 Login")
    def login_dialog():
        st.markdown("### Welcome Back")
        st.markdown("Please sign in to your account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")

        if st.button("Login", key="login_dialog"):
            if not email or not password:
                st.warning("필수 항목을 입력해주세요.")
            elif email == "sw_admin" and password == "admin123":
                # ✅ 관리자 계정은 DB 없이 바로 로그인
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = email
                st.session_state["user_name"] = "관리자"
                st.session_state["role"] = "admin"
                st.session_state["page"] = "main"
                st.success("관리자님, 어서오세요.")
                st.rerun()
            else:
                # ✅ 일반 사용자 로그인 (DB 조회)
                try:
                    user = login_user(email, password)
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user_email"] = email
                        st.session_state["user_name"] = user[1]
                        st.session_state["role"] = "user"
                        st.session_state["page"] = "main"
                        st.success(f"{user[1]}님, 환영합니다!")
                        st.rerun()
                    else:
                        st.error("ID 또는 비밀번호 오류")
                except Exception as e:
                    st.error("로그인에 실패했습니다.")


    # 회원가입 팝업
    @st.dialog("📝 Register")
    def signup_dialog():
        st.markdown("### Join Us")
        st.markdown("Create your account")
        name = st.text_input("Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Register", key="register_dialog"):
            if not name or not email or not password:
                st.warning("필수 항목을 입력해주세요.")
            elif len(password) < 3:
                st.warning("비밀번호는 최소 3자 이상이어야 합니다.")
            elif len(set(password)) == 1:   
                st.warning("비밀번호에 동일한 문자 반복은 사용할 수 없습니다.") 
            else:
                try:
                    success = register_user(name, email, password)
                    if success:
                        st.success("회원가입에 성공했습니다.")
                    else:
                        st.error("이미 존재하는 ID입니다.")
                except Exception as e:
                    st.error("회원가입에 실패했습니다.")

    # Final Test 관련 경고 메시지 출력 (메인 화면에 띄움)
    if st.session_state.get("show_login_warning"):
        st.warning("로그인이 필요한 기능입니다.")
        st.session_state.show_login_warning = False  

    if st.session_state.get("show_final_test_error"):
        st.error("문제를 불러오지 못했습니다.")
        st.session_state.show_final_test_error = False
        
    # 사이드바
    with st.sidebar:
        st.header("Menu")

        # Wordbook 선택
        with st.expander("📚Wordbook"):
            st.markdown("choose your wordbook")
            if st.button("📗수능", key="suneung_btn"):
                st.session_state.page = "wordbook_high"
                st.session_state.wordbook = load_words_from_excel(SUNEUNG_FILE)
                st.rerun()
            if st.button("📕TOEIC", key="toeic_btn"):
                st.session_state.page = "wordbook_toeic"
                st.session_state.wordbook = load_words_from_excel(TOEIC_FILE)
                st.rerun()
            if st.button("📘TEPS", key="teps_btn"):
                st.session_state.page = "wordbook_teps"
                st.session_state.wordbook = load_words_from_excel(TEPS_FILE)
                st.rerun()
            st.markdown("---")
            if st.button("📅 Todays words", key="today_word_btn"):
                st.session_state.page = "todays_word"
                st.rerun()

        # Practice Test
        with st.expander("🖋️ Practice Test"):
            st.markdown("""
                <style>
                div.stButton > button {
                    width: 100%;
                    padding: 6px;
                    margin-top: 4px;
                    font-size: 14px;
                }
                </style>
            """, unsafe_allow_html=True)

            source = st.session_state.get("test_type", None)
            if st.button("🔁 Restart Test"):
                st.success("시험을 재시작합니다.")
                if source == "suneung":
                    st.session_state.questions = load_words_from_excel(SUNEUNG_FILE)
                elif source == "toeic":
                    st.session_state.questions = load_words_from_excel(TOEIC_FILE)
                elif source == "teps":
                    st.session_state.questions = load_words_from_excel(TEPS_FILE)
                elif source == "today":
                    st.session_state.questions = get_today_words()
                else:
                    st.warning("이전에 본 시험 유형을 알 수 없습니다.")

                st.session_state.q_index = 0
                st.session_state.score = 0
                st.session_state.correct = 0
                st.session_state.wrong = 0
                st.session_state.wrong_words = []
                st.session_state.page = "test"
                st.rerun()

            if st.button("📚 Go to wordbook"):
                test_type = st.session_state.get("test_type")
                if test_type == "suneung":
                    st.session_state.page = "wordbook_high"
                elif test_type == "toeic":
                    st.session_state.page = "wordbook_toeic"
                elif test_type == "teps":
                    st.session_state.page = "wordbook_teps"
                elif source == "today":
                    st.session_state.page = "todays_word"
                else:
                    st.warning("먼저 시험 유형이 설정되어야 합니다.")

        st.markdown("---")
        # Final Test 버튼
        if st.button("📒 skill Test"):
        # 비로그인 사용자 예외 처리
            if not st.session_state.get("logged_in"):
                st.session_state.show_login_warning = True
            else:
                try:
                    # 단어 불러오기
                    suneung = load_words_from_excel("data/suneung.csv")   
                    toeic = load_words_from_excel("data/toeic.csv")
                    teps = load_words_from_excel("data/teps.csv")

                    all_words = suneung + toeic + teps

                    if not all_words:
                        st.session_state.show_final_test_error = True
                    else:
                        # 세션 초기화
                        st.session_state.questions = random.sample(all_words, min(20, len(all_words)))
                        st.session_state.test_type = "final"
                        st.session_state.q_index = 0
                        st.session_state.score = 0
                        st.session_state.correct = 0
                        st.session_state.wrong = 0
                        st.session_state.wrong_words = []
                        st.session_state.show_ranking = True
                        st.session_state.page = "test"
                        st.rerun()

                except Exception as e:
                    st.session_state.show_final_test_error = True


        # 메인으로 이동
        if st.button("Go to main", key="main_nav_btn"):
            for key in ["test_type", "q_index", "score", "correct", "wrong", "wrong_words", "questions"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = "main"
            st.rerun()

        # 로그인 여부에 따라 표시
        if st.session_state.get("logged_in"):
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

            # 관리자 로그인 시 사용자 관리 팝업
            if st.session_state.get("role") == "admin":
                with st.expander("🛡️ 사용자 관리"):
                    users = get_all_users()
                    for user_id, name, email in users:
                        if email == "sw_admin":
                            continue
                        col1, col2 = st.columns([6, 2])
                        with col1:
                            st.write(f"{name} ({email})")
                        with col2:
                            if st.button("삭제", key=f"delete_{user_id}"):
                                try:
                                    conn = sqlite3.connect('users.db')
                                    c = conn.cursor()
                                    c.execute("DELETE FROM users WHERE email = ?", (email,))
                                    c.execute("DELETE FROM user_stats WHERE email = ?", (email,))
                                    conn.commit()
                                    conn.close()
                                    st.success(f"{name} 삭제됨!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"삭제 실패: {str(e)}")

            st.markdown(f"<div style='text-align: margin-top: 10px;'>👤 <b>{st.session_state.get('user_name')}</b> 님</div>", unsafe_allow_html=True)
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", key="login_sidebar"):
                    login_dialog()
            with col2:
                if st.button("Register", key="register_sidebar"):
                    signup_dialog()
