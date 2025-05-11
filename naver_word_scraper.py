# naver_word_scraper.py
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time
import datetime

driver_path = "C:/Users/서민경/Downloads/msedgedriver.exe"

options = Options()
options.add_argument("--headless")  # 브라우저 안 띄우고 실행
service = Service(driver_path)
driver = webdriver.Edge(service=service, options=options)

url = "https://wquiz.dict.naver.com/enkodict/today/quiz.dict#tab=1"
driver.get(url)
time.sleep(5)

words = []
word_boxes = driver.find_elements(By.CLASS_NAME, "word_box")
for box in word_boxes:
    try:
        word = box.find_element(By.CLASS_NAME, "question_text__nQaVt").text
        meaning = box.find_element(By.CLASS_NAME, "mean_text__uZ4jI").text
        words.append((word, meaning))
    except:
        continue

driver.quit()

# 결과 파일로 저장
today = datetime.date.today().isoformat()
with open(f"today_words_{today}.txt", "w", encoding="utf-8") as f:
    for word, meaning in words:
        f.write(f"{word} - {meaning}\n")
