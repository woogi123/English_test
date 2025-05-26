import streamlit as st
from word_data import load_words_from_excel
from admin import show_admin_panel

import requests
from bs4 import BeautifulSoup
from googletrans import Translator

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import re
import random

import csv

def get_exam_1(url, header):
    headers = {'User-Agent': header}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find('div', class_='tt_article_useless_p_margin contents_style')
    if not content_div:
        return []

    results = []
    h3_tags = content_div.find_all('h3')
    for h3 in h3_tags:
        word = h3.get_text(strip=True)
        word = re.sub(r'^\d+\.\s*', '', word)
        ul = h3.find_next_sibling('ul')
        if not ul:
            continue
        items = ul.find_all('li')
        if len(items) < 3:
            continue
        meaning = items[0].get_text(strip=True)
        example_full = items[2].get_text(strip=True)


        if '.”(' in example_full:
            eng_part, kor_part = example_full.split('.”(', 1)
            eng_sentence = eng_part.strip() + '.”'
            kor_translation = kor_part.rstrip(')').strip()
        else:
            eng_sentence = example_full
            kor_translation = ''

        results.append({
            "단어": word,
            "뜻": meaning,
            "예문": eng_sentence,
            "해석": kor_translation
        })
    return results


def get_exam_2(url, header):
    headers = {'User-Agent': header}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    content_div = soup.find('div', class_='tt_article_useless_p_margin contents_style')
    if not content_div:
        return []

    results = []
    p_tags = content_div.find_all('p')
    for p in p_tags:
        word_text = p.get_text(strip=True)
        if not word_text or not any(char.isdigit() for char in word_text):
            continue
        word = word_text.split('.', 1)[-1].strip()
        ul = p.find_next_sibling('ul')
        if not ul:
            continue
        meaning = None
        example = None
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            if text.startswith("뜻:"):
                meaning = text.replace("뜻:", "").strip()
            elif text.startswith("예문:"):
                example = text.replace("예문:", "").strip()
        if word and meaning and example:
            results.append({
                "단어": word,
                "뜻": meaning,
                "예문": example
            })
    return results

urls = [
    'https://hyunjae0606.tistory.com/39',
    'https://hyunjae0606.tistory.com/40',
    'https://hyunjae0606.tistory.com/41',
]
headers = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/136.0.0.0'
]

result_exam_2 = []
for i in range(len(urls)):
    result_exam_2.extend(get_exam_2(urls[i], headers[i]))

translator = Translator()

for item in result_exam_2:
    try:
        translated = translator.translate(item["예문"], src='en', dest='ko')
        item["해석"] = translated.text
    except Exception as e:
        item["해석"] = "(번역 오류)"
        print(f"번역 오류 발생: {e}")


urls = [
    'https://hyunjae0606.tistory.com/3', 
    'https://hyunjae0606.tistory.com/4',
]
headers = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
]
result_exam_1 = []
for i in range(len(urls)):
    result_exam_1.extend(get_exam_1(urls[i], headers[i]))

def get_exam_3():
    url = "https://m.blog.naver.com/minheuicho/223618380891"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all('div', class_='se-module se-module-text')

    results = []
    current_item = {}
    for div in divs:
        paragraphs = div.find_all('p', class_='se-text-paragraph se-text-paragraph-align-justify')
        for p in paragraphs:
            span = p.find('span')
            if not span:
                continue
            text = span.get_text(strip=True)
            if '.' in text and '-' in text and not text.startswith('해석') and not text.startswith('문장'):
                if current_item:
                    if all(key in current_item for key in ['단어', '뜻', '예문', '해석']):
                        results.append(current_item)
                current_item = {}
                parts = text.split('-', 1)
                current_item['단어'] = parts[0].split('.', 1)[-1].strip()
                current_item['뜻'] = parts[1].strip()
            elif text.startswith('문장:'):
                current_item['예문'] = text.replace('문장:', '').strip()
            elif text.startswith('해석:'):
                current_item['해석'] = text.replace('해석:', '').strip()
    if current_item and all(key in current_item for key in ['단어', '뜻', '예문', '해석']):
        results.append(current_item)

    return results

result_exam_3 = get_exam_3()

merged_result = result_exam_1 + result_exam_2 + result_exam_3

dict_result = []

for item in merged_result:
    entry = {
        "word": item.get("단어"),
        "meaning": item.get("뜻"),
        "example": item.get("예문")
    }
    if "해석" in item:
        entry["example_meaning"] = item.get("해석")
    dict_result.append(entry)


def get_variants(word):
    return list(filter(None, [
        word,
        word + 's',
        word + 'ed',
        word + 'ing',
        word + 'es',
        word + 'd' if word.endswith('e') else ''
    ]))

dict_result = []

drop_words = {"investigate", "omit", "commit", "explore"}

for item in merged_result:
    word = item.get("단어")
    if word.lower() in drop_words:
        continue

    # 접두사 "뜻: " 또는 "예문: " 제거
    meaning = item.get("뜻", "").removeprefix("뜻: ").strip()
    example = item.get("예문", "").removeprefix("예문: ").strip()
    example_meaning = item.get("해석", "").removeprefix("해석: ").strip()

    variants = get_variants(word)
    pattern = r'\b(' + '|'.join(map(re.escape, variants)) + r')\b'
    replaced_example = re.sub(pattern, "_________", example, flags=re.IGNORECASE)

    entry = {
        "word": word,
        "meaning": meaning,
        "example": replaced_example,
    }

    if example_meaning:
        entry["example_meaning"] = example_meaning

    dict_result.append(entry)

with open("suneung.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["word", "meaning", "example", "example_meaning"])
    writer.writeheader()
    for entry in dict_result:
        writer.writerow(entry)


def run_wordbook_high():
    # 수능 단어장 파일 경로
    FILE_PATH = "suneung.csv"

    # session_state에 단어장 초기화 + 예외 흐름 추가
    try:
        if "wordbook" not in st.session_state:
            st.session_state.wordbook = load_words_from_excel(FILE_PATH)
            if not st.session_state.wordbook:  # 빈 리스트일 때
                st.error("단어 목록을 불러올 수 없습니다.")
                return
    except Exception as e:
        st.error("단어 목록을 불러올 수 없습니다.")
        return
    
    if "keep_words" not in st.session_state:
        st.session_state.keep_words = []

    st.title("📗수능")

    # 관리자 모드
    if st.session_state.get("role") == "admin":
        st.session_state.dataset = "suneung"  
        show_admin_panel()

    # 시험으로 이동 버튼
    if st.button("📝 taking a test", key="to_test_wordbook"):
        st.session_state["test_type"] = "suneung"
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

    # ✅ 탭 나누기
    tab1, tab2 = st.tabs(["📖 Wordbook", "📌"])

    with tab1:
        st.subheader("전체 단어")
        for i, item in enumerate(st.session_state.wordbook): 
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{item['word']}** - {item['meaning']}")
            with col2:
                if st.button("📌 Keep", key=f"keep_{i}"):
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