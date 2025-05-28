import streamlit as st
from word_data import load_words_from_excel, save_words_to_excel

def add_word():
    with st.form(key="add_word_form"):
        new_word = st.text_input("영어 단어")
        new_meaning = st.text_input("뜻")
        new_example = st.text_input("예문")
        submitted = st.form_submit_button("단어 추가하기")
        if submitted:
            if not new_word or not new_meaning or not new_example:
                st.warning("항목을 모두 입력하세요.")
            else:
                try:
                    st.session_state.wordbook.append({
                        "word": new_word,
                        "meaning": new_meaning,
                        "example": new_example
                    })
                    save_words_to_excel(st.session_state.dataset, st.session_state.wordbook)
                    st.success(f"단어 '{new_word}' 추가 완료!")
                    #st.rerun()
                except Exception:
                    st.error("단어 추가에 실패했습니다.")


def delete_word():
    with st.form(key="delete_word_form"):
        target = st.text_input("삭제할 단어 (영어)")
        submitted = st.form_submit_button("삭제하기")
        if submitted:
            if not target:
                st.warning("항목을 모두 입력하세요.")
            else:
                try:
                    before = len(st.session_state.wordbook)
                    st.session_state.wordbook = [w for w in st.session_state.wordbook if w["word"] != target]
                    after = len(st.session_state.wordbook)
                    if before != after:
                        save_words_to_excel(st.session_state.dataset, st.session_state.wordbook)
                        st.success(f"'{target}' 단어 삭제 완료!")
                        #st.rerun()
                    else:
                        st.warning(f"'{target}' 단어를 찾을 수 없습니다")
                except Exception:
                    st.error("단어 삭제에 실패했습니다.")


def edit_word():
    show_edit_list = st.checkbox("✏️ 단어 목록", value=False)

    if show_edit_list:
        for i, w in enumerate(st.session_state.wordbook):
            with st.expander(f"{w['word']} 수정"):
                new_word = st.text_input("영어 단어", value=w["word"], key=f"edit_word_{i}")
                new_meaning = st.text_input("뜻", value=w["meaning"], key=f"edit_meaning_{i}")
                new_example = st.text_input("예문", value=w.get("example", ""), key=f"edit_example_{i}")

                if st.button("수정 완료", key=f"submit_edit_{i}"):
                    if not new_word or not new_meaning:
                        st.warning("항목을 모두 입력하세요.")
                    else:
                        try:
                            st.session_state.wordbook[i] = {
                                "word": new_word,
                                "meaning": new_meaning,
                                "example": new_example
                            }
                            save_words_to_excel(st.session_state.dataset, st.session_state.wordbook)
                            st.success(f"{new_word} 수정 완료!")
                            #st.rerun()
                        except Exception:
                            st.error("단어 수정에 실패했습니다.")



def show_admin_panel():
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✏️ 단어 수정"):
            st.session_state.show_edit = True
            st.session_state.show_add = False
            st.session_state.show_delete = False
            st.session_state.show_upload = False
    with col2:
        if st.button("➕ 단어 추가"):
            st.session_state.show_edit = False
            st.session_state.show_add = True
            st.session_state.show_delete = False
            st.session_state.show_upload = False
    with col3:
        if st.button("🗑️ 단어 삭제"):
            st.session_state.show_edit = False
            st.session_state.show_add = False
            st.session_state.show_delete = True
            st.session_state.show_upload = False

    if st.session_state.get("show_add"):
        st.markdown("## ➕ 단어 추가")
        add_word()
    if st.session_state.get("show_delete"):
        st.markdown("## 🗑️ 단어 삭제")
        delete_word()
    if st.session_state.get("show_edit"):
        st.markdown("## ✏️ 단어 수정")
        edit_word()