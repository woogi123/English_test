import streamlit as st
import pandas as pd
import random
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
import time

def load_words_from_excel(file):
    """엑셀 파일에서 단어 리스트를 로드"""
    try:
        df = pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(file, encoding="cp949")  

    df.columns = df.columns.str.strip().str.lower()

    expected_cols = {'word', 'example', 'meaning'}
    actual_cols = set(df.columns)
    if not expected_cols.issubset(actual_cols):
        raise ValueError("엑셀 파일에 'word', 'example', 'meaning' 컬럼이 필요합니다.")

    words_list = []
    for _, row in df.iterrows():
        word_entry = {
            "word": str(row["word"]).strip(),
            "meaning": str(row["meaning"]).strip(),
            "example": str(row["example"]).strip()
        }
        words_list.append(word_entry)

    return words_list

def save_words_to_excel(dataset_name, words_list):
    import pandas as pd
    file_path = f"{dataset_name}.csv"
    df = pd.DataFrame(words_list)
    df.to_csv(file_path, index=False)


# word_data.py

def get_today_words_from_naver():
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent=Mozilla/5.0")

    # chromedriver 경로를 본인 PC에 맞게 설정하세요
    service = ChromeService(executable_path="C:\\Users\\lsj55\\Desktop\\eng_test\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://search.naver.com/search.naver?query=오늘의+단어"
        driver.get(url)
        time.sleep(2)

        words = []
        word_links = driver.find_elements(By.CSS_SELECTOR, "a.word")

        for link in word_links:
            try:
                word = link.find_element(By.TAG_NAME, "strong").text.strip()
                meaning = link.find_element(By.XPATH, "./following-sibling::span[@class='mean']").text.strip()
                words.append({"word": word, "meaning": meaning, "example": ""})
            except Exception as e:
                print(f"❗ 오류 발생: {e}")
                continue

        return words

    finally:
        driver.quit()


def get_today_words():
    try:
        words = get_today_words_from_naver()
        if not words:
            return [{"word": "No words found", "meaning": "오늘의 단어를 찾을 수 없습니다.", "example": ""}]
        return words
    except Exception as e:
        return [{"word": "Error", "meaning": f"크롤링 중 오류 발생: {e}", "example": ""}]

