import streamlit as st
from word_data import load_words_from_excel
from admin import show_admin_panel
import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import csv
import re

def get_today_words_from_naver():
    options = ChromeOptions()
    options.add_argument('--headless')  # 창 없이 실행
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent=Mozilla/5.0")

    # 여기 각자 컴퓨터에 맞게 수정!
    service = ChromeService(executable_path="C:/Users/lsj55/Desktop/eng_test/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://search.naver.com/search.naver?query=오늘의+단어"
        driver.get(url)
        time.sleep(2)  # 로딩 대기

        words = []

        # 모든 단어 항목 선택
        word_links = driver.find_elements(By.CSS_SELECTOR, "a.word")

        for link in word_links:
            try:
                word = link.find_element(By.TAG_NAME, "strong").text.strip()
                # 뜻은 link 다음에 나오는 <span class="mean"> 요소임
                meaning = link.find_element(By.XPATH, "./following-sibling::span[@class='mean']").text.strip()
                words.append((word, meaning))
            except Exception as e:
                print(f"❗ 오류 발생: {e}")
                continue

        return words

    finally:
        driver.quit()


def get_teps(driver_path="chromedriver.exe"):
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0")

    service = ChromeService(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://blog.naver.com/lblucy/223865867643")

    driver.switch_to.frame("mainFrame")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # 원하는 span만 추출
    spans = soup.find_all('span', class_='se-fs- se-ff-')
    texts = [span.get_text(strip=True) for span in spans if span.get_text(strip=True)]

    results = []
    temp = {}

    for text in texts:
        if '의미 :' in text:
            temp['의미'] = text.replace('의미 :', '').strip()
        elif '예문 :' in text:
            temp['예문'] = text.replace('예문 :', '').strip()
        elif '뜻 :' in text:
            temp['뜻'] = text.replace('뜻 :', '').strip()
            if '단어' in temp and '의미' in temp and '예문' in temp:
                results.append(temp)
                temp = {}
        else:
            # '단어'는 의미, 예문, 뜻이 아닌 일반 텍스트로 간주
            temp = {'단어': text}

    return results

def trans_teps_data(text_lines):
    """
    text_lines: 블로그에서 추출한 한 줄짜리 문자열 리스트
                [단어, '의미 : xxx', '예문 : yyy', '뜻 : zzz', ...] 패턴으로 반복된다고 가정.
    return     : [{'word': ..., 'meaning': ..., 'example': ..., 'example_meaning': ...}, ...]
    """
    parsed = []
    i = 0

    while i < len(text_lines):
        word = text_lines[i].strip()

        # 최소 3줄 더 있어야 의미/예문/뜻이 붙어 있다고 판단
        if (i + 3 < len(text_lines)
            and text_lines[i + 1].startswith("의미")
            and text_lines[i + 2].startswith("예문")
            and text_lines[i + 3].startswith("뜻")):

            meaning = re.sub(r"^의미\s*:", "", text_lines[i + 1]).strip()
            example = re.sub(r"^예문\s*:", "", text_lines[i + 2]).strip()
            example_meaning = re.sub(r"^뜻\s*:", "", text_lines[i + 3]).strip()

            parsed.append({
                "word": word,
                "meaning": meaning,
                "example": example,
                "example_meaning": example_meaning
            })

            i += 4   # 다음 단어 블록으로 이동
        else:
            # 패턴이 깨진 경우 한 줄만 넘기고 계속 탐색
            i += 1

    return parsed


def get_variants(word):
    return list(filter(None, [
        word,
        word + 's',
        word + 'ed',
        word + 'ing',
        word + 'es',
        word + 'd' if word.endswith('e') else ''
    ]))

raw_data = get_teps("C:/Users/lsj55/Desktop/eng_test/chromedriver-win64/chromedriver.exe")
dict_result = []

for item in raw_data:
    word = item.get("단어")
    meaning = item.get("뜻")
    example = item.get("예문")
    example_meaning = item.get("해석", "")

    pattern = r'\b' + re.escape(word) + r'\b'
    replaced_example = re.sub(pattern, "_________", example, flags=re.IGNORECASE)

    entry = {
        "word": word,
        "meaning": meaning,
        "example": replaced_example,
    }

    if example_meaning:
        entry["example_meaning"] = example_meaning

    dict_result.append(entry)

with open("teps.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["word", "meaning", "example", "example_meaning"])
    writer.writeheader()
    for entry in dict_result:
        writer.writerow(entry)


# 실행
word_list = get_today_words_from_naver()
print(f"총 {len(word_list)}개 단어 추출됨.")
for word, meaning in word_list:
    print(f"{word} - {meaning}")

def run_wordbook_teps():
   
    # TEPS 단어장 파일 경로
    FILE_PATH = "teps.csv"

    # session_state에 단어장 초기화 + 예외 흐름 추가
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

    st.title("📘TEPS")

    # 관리자 모드
    if st.session_state.get("role") == "admin":
        st.session_state.dataset = "teps" 
        show_admin_panel()

    # 시험으로 이동 버튼
    if st.button("📝 taking a test", key="to_test_wordbook"):
        st.session_state["test_type"] = "teps"
        st.session_state.questions = random.sample(load_words_from_excel(FILE_PATH), 20)
        st.session_state.page = "test"
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.correct = 0
        st.session_state.wrong = 0
        st.session_state.wrong_words = []
        st.session_state.show_ranking = False
        
        # 이전 테스트 상태들 초기화
        st.session_state.submitted = False
        st.session_state.answer_input = ""
        st.session_state.feedback_message = ("info", "")
        
        st.rerun()

    # 탭 나누기
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