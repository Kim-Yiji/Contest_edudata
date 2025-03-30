### 📦 모듈 & 환경설정
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time

### 🔧 사용자 설정
NEWS_KEYWORD = "(교육부)"  # 분석 키워드
DOWNLOAD_DIR_NAME = "downloads"  # 다운로드 폴더명 (현재 작업 디렉토리 기준)

### 💾 다운로드 경로 설정
download_path = os.path.join(os.getcwd(), DOWNLOAD_DIR_NAME)
os.makedirs(download_path, exist_ok=True)

### 🔐 로그인 정보 로딩 (.env에서)
load_dotenv()
USER_EMAIL = os.getenv("BIGKINDS_EMAIL")
USER_PASSWORD = os.getenv("BIGKINDS_PASSWORD")

### 🌐 크롬 드라이버 설정
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)
options.add_experimental_option("detach", True)
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

### 🧩 공통 함수 정의
def scroll_and_click(by, value):
    element = wait.until(EC.element_to_be_clickable((by, value)))
    driver.execute_script("""
        const rect = arguments[0].getBoundingClientRect();
        window.scrollBy({
            top: rect.top - (window.innerHeight / 2),
            left: 0,
            behavior: 'smooth'
        });
    """, element)
    WebDriverWait(driver, 3).until(EC.visibility_of(element))
    element.click()
    return element
def login(driver, wait, email, password):
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "topMembership")))
    driver.execute_script("""
        document.querySelector('.topMembership .new_userInfo_view').style.display = 'block';
    """)
    login_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[text()="로그인"]')))
    login_link.click()

    email_input = wait.until(EC.visibility_of_element_located((By.ID, 'login-user-id')))
    email_input.click()
    email_input.clear()
    for char in email:
        email_input.send_keys(char)
        time.sleep(0.01)

    password_input = wait.until(EC.visibility_of_element_located((By.ID, 'login-user-password')))
    password_input.click()
    password_input.clear()
    for char in password:
        password_input.send_keys(char)
        time.sleep(0.01)

    login_button = wait.until(EC.element_to_be_clickable((By.ID, "login-btn")))
    login_button.click()
    print("✅ 로그인 완료")
    time.sleep(3)

### 🚀 전체 자동화 흐름 시작
driver.get("https://www.bigkinds.or.kr/v2/news/index.do")

### 🔐 로그인
login(driver, wait, USER_EMAIL, USER_PASSWORD)

### 🔄 뉴스 검색 페이지 재로딩
driver.get("https://www.bigkinds.or.kr/v2/news/index.do")
wait.until(EC.presence_of_element_located((By.ID, "total-search-key")))

### 🔍 검색 키워드 입력
search_input = driver.find_element(By.ID, "total-search-key")
search_input.click()
search_input.clear()
for char in NEWS_KEYWORD:
    search_input.send_keys(char)
    time.sleep(0.02)
print(f"🔍 검색어 '{NEWS_KEYWORD}' 입력 완료")

### 📰 뉴스 필터 설정
scroll_and_click(By.XPATH, '//label[@for="전국일간지"]')
print("✅ 전국일간지 선택 완료")

scroll_and_click(By.XPATH, '//div[@class="add-depth add-depth-day f-center" and @data-gubuncode="30"]')
wait.until(EC.presence_of_element_located((By.XPATH, '//label[@for="do2"]')))
print("✅ 지역일간지 + 클릭 완료")

scroll_and_click(By.XPATH, '//label[@for="do2"]')
print("✅ 경기 지역 선택 완료")

### 🧠 분석 적용 및 실행
scroll_and_click(By.XPATH, '//*[@id="search-foot-div"]/div[2]/button[2]')
wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="news-results-tab"]/div[1]/div[1]/button[3]')))
print("📌 '적용하기' 버튼 클릭 완료")

scroll_and_click(By.XPATH, '//*[@id="news-results-tab"]/div[1]/div[1]/button[3]')
print("📊 '뉴스분석' 버튼 클릭 완료")
time.sleep(1.5)

### 📥 엑셀 다운로드
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(0.5)

download_button = wait.until(EC.element_to_be_clickable((
    By.XPATH, '//button[contains(@class, "news-download-btn") and contains(text(), "엑셀 다운로드")]'
)))
download_button.click()
print("📥 '엑셀 다운로드' 버튼 클릭 완료")
