import streamlit as st
from db import record_test_result, get_user_stats, get_top_rankings

def run_result_rank():
    # 세션에서 값 불러오기
    score = st.session_state.get("score", 0)
    correct = st.session_state.get("correct", 0)
    wrong = st.session_state.get("wrong", 0)
    wrong_words = st.session_state.get("wrong_words", [])
    show_ranking = st.session_state.get("show_ranking", True)
    
    # 로그인 사용자 정보
    user_email = st.session_state.get("user_email")
    user_name = st.session_state.get("user_name")

  # 테스트 결과 저장 및 랭킹 데이터 (메시지는 탭 안에서만 띄움)
    ranking_error = False  # 플래그 설정
    if user_email and user_name:
        try:
            record_test_result(user_email, user_name, score)
            total, passed = get_user_stats(user_email)
            ranking_data = get_top_rankings()
        except Exception as e:
            ranking_error = True
            total, passed = 0, 0
            ranking_data = []
    else:
        user_logged_in = False
        total, passed = 0, 0
        ranking_data = []



    # 탭 구성
    if show_ranking:
        tab1, tab2, tab3 = st.tabs(["✅ Test result", "📊 Ranking" , "❌ Review"])
    else:
        tab1, tab2 = st.tabs(["✅ Test result", "❌ Review" ])

    # 결과 탭
    with tab1:
        st.subheader("✅ Test result Summury")
        st.markdown(f"### 점수: **{score}점**")
        st.markdown(f"- 맞은 개수: {correct} / {correct + wrong}")
        st.markdown(f"- 틀린 개수: {wrong}")
        st.markdown("---")
        st.markdown("### 📊 Total")
        if not user_email:
                st.warning("로그인이 필요한 기능입니다.")
        else :
            st.info(f"🔁 총 테스트 횟수: **{total}회**  \n✅ 당신의 랭킹: **{passed}회**")
        # **이 부분 나중에 your ranking 으로 바꿔서 보여주기**

    # 랭킹+리뷰 탭
    if show_ranking:
        # 랭킹 탭
        with tab2:
            st.subheader("📊 Ranking")
            if not user_email:
                st.warning("로그인이 필요한 기능입니다.")  
            elif ranking_error:
                st.error("랭킹 로딩에 실패했습니다.")
            elif not ranking_data:
                st.info("랭킹 데이터가 없습니다.")
            else:
                for idx, user in enumerate(ranking_data, start=1):
                    st.markdown(f"{idx}위 - **{user[0]}** : {user[1]}회")

        # 리뷰 탭
        with tab3:
            st.subheader("❌ Review")
            for w in wrong_words:
                test_type = st.session_state.get("test_type")
                if test_type == "today":
                    st.markdown(f"""
                    <div style='padding: 10px; background-color: #f7f7f7; margin-bottom: 10px; border-radius: 6px;'>
                        <b>{w['word']}</b><br>
                        뜻: {w['meaning']}<br>
                    </div>
                    """, unsafe_allow_html=True)
                else :
                    st.markdown(f"""
                    <div style='padding: 10px; background-color: #f7f7f7; margin-bottom: 10px; border-radius: 6px;'>
                        <b>{w['word']}</b><br>
                        뜻: {w['meaning']}<br>
                        예문: <i>{w['example']}</i>
                    </div>
                    """, unsafe_allow_html=True)
    # 리뷰 탭만
    else:
        with tab2:
            st.subheader("❌ Review")
            for w in wrong_words:
                test_type = st.session_state.get("test_type")
                if test_type == "today":
                    st.markdown(f"""
                    <div style='padding: 10px; background-color: #f7f7f7; margin-bottom: 10px; border-radius: 6px;'>
                        <b>{w['word']}</b><br>
                        뜻: {w['meaning']}<br>
                    </div>
                    """, unsafe_allow_html=True)
                else :
                    st.markdown(f"""
                    <div style='padding: 10px; background-color: #f7f7f7; margin-bottom: 10px; border-radius: 6px;'>
                        <b>{w['word']}</b><br>
                        뜻: {w['meaning']}<br>
                        예문: <i>{w['example']}</i>
                    </div>
                    """, unsafe_allow_html=True)