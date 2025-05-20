from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

options = ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')

# 경로는 너가 사용한 거 그대로
service = ChromeService(executable_path="C:/Users/lsj55/Desktop/eng_test/chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com")
print(driver.title)  # 👉 여기서 'Google'이 출력되면 100% 성공!
driver.quit()
