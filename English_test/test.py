import streamlit as st
import random
from word_data import load_words_from_excel, get_today_words

def run_test():
    if "test_type" not in st.session_state:
        st.error("❗ 테스트 유형이 지정되지 않았습니다. 단어장을 먼저 선택하세요.")
        return

    test_type = st.session_state.test_type

    # ✅ 엑셀 기반 데이터 불러오기 + 예외 흐름 추가
    try:
        if test_type == "suneung":
            if "questions" not in st.session_state:
                data = load_words_from_excel("suneung.csv")
                if not data:
                    st.error("단어를 불러올 수 없습니다.")
                    return
                st.session_state.questions = random.sample(data, min(20, len(data)))

        elif test_type == "toeic":
            if "questions" not in st.session_state:
                data = load_words_from_excel("toeic.csv")
                if not data:
                    st.error("단어를 불러올 수 없습니다.")
                    return
                st.session_state.questions = random.sample(data, min(20, len(data)))

        elif test_type == "teps":
            if "questions" not in st.session_state:
                data = load_words_from_excel("teps.csv")
                if not data:
                    st.error("단어를 불러올 수 없습니다.")
                    return
                st.session_state.questions = random.sample(data, min(20, len(data)))

        elif test_type == "today":
            data = get_today_words()
            if not data:
                st.error("단어를 불러올 수 없습니다.")
                return
            st.session_state.questions = data

        elif test_type == "final":
            pass

        else:
            st.error("❗ 유효하지 않은 테스트 유형입니다.")
            return

    except Exception as e:
        st.error("로딩에 실패했습니다.")
        return


    questions = st.session_state.questions

    # ✅ 상태 초기화
    if "wrong_words" not in st.session_state:
        st.session_state["wrong_words"] = []
    if "score" not in st.session_state:
        st.session_state["score"] = 0
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "answer_input" not in st.session_state:
        st.session_state.answer_input = ""

    current_q = questions[st.session_state.q_index]
    total = len(questions)
    progress = (st.session_state.q_index + 1) / total

    st.progress(progress)
    st.markdown(f"### 문제 {st.session_state.q_index + 1}")

    if not st.session_state.submitted:
        # 문제 표시
        if test_type == "today":
            st.markdown(f"**뜻:** {current_q['meaning']}")
        else:
            st.markdown(f"**예문:** {current_q['example']}")
            st.markdown(f"**뜻:** {current_q['meaning']}")

        # 정답 입력창 (기존 값 유지)
        st.session_state.answer_input = st.text_input(
            "정답은?" if test_type == "today" else "빈칸에 들어갈 단어는?",
            value=st.session_state.answer_input,
            key=f"input_{st.session_state.q_index}"
        )

        # 제출 버튼 + 예외 흐름 추가
        if st.button("제출하기", key=f"submit_{st.session_state.q_index}"):
            user_answer = st.session_state.answer_input.strip().lower()
            try:
                correct_answer = current_q["word"].strip().lower()

                if user_answer == "":
                    st.warning("정답을 입력해주세요.")
                else:
                    if user_answer == correct_answer:
                        st.session_state["feedback_message"] = ("success", "정답입니다!")
                        st.session_state.score += 1
                    else:
                        st.session_state["feedback_message"] = ("error", f"오답입니다. 정답: {correct_answer}")
                        st.session_state.wrong_words.append(current_q)

                    st.session_state.submitted = True
                    st.rerun()

            except Exception as e:
                st.error("채점을 실패했습니다.")


    else:
        # 제출 결과 표시
        msg_type, msg_text = st.session_state.get("feedback_message", ("info", ""))
        if msg_type == "success":
            st.success(msg_text)
        elif msg_type == "error":
            st.error(msg_text)

        # 다음 문제로 이동 버튼
        if st.button("👉 다음 문제로 넘어가기"):
            if st.session_state.q_index < total - 1:
                st.session_state.q_index += 1
                st.session_state.submitted = False
                st.session_state.answer_input = ""
                st.session_state["feedback_message"] = ("info", "")
                st.rerun()
            else:
                st.session_state["correct"] = st.session_state.score
                st.session_state["wrong"] = total - st.session_state.score
                st.session_state["page"] = "result"
                st.session_state.submitted = False
                st.session_state.answer_input = ""
                st.session_state["feedback_message"] = ("info", "")
                st.rerun()