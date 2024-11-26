import logging
from bs4 import BeautifulSoup
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, text
import pandas as pd
import warnings
import os
import glob
import openpyxl

# 로깅 설정
logging.basicConfig(
    filename='/home/ubuntu/hotel/hotel_rating.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# SQLAlchemy 엔진 생성 함수
def create_sqlalchemy_engine():
    db_url = 'mysql+pymysql://root:1231@13.125.203.0:3306/crawling?charset=utf8mb4'
    engine = create_engine(db_url, echo=False)
    logger.info("SQLAlchemy engine created.")
    return engine

# 웹 드라이버 설정
def setup_driver(download_dir):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36")
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    logger.info("Web driver set up completed.")
    return driver

# 다운로드 완료 대기 함수
def wait_for_download_to_complete(download_dir, timeout=60):
    seconds = 0
    while True:
        downloading_files = glob.glob(os.path.join(download_dir, '*.crdownload'))
        if not downloading_files:
            logger.info("Download complete.")
            break
        time.sleep(1)
        seconds += 1
        if seconds > timeout:
            logger.error("Download timed out.")
            break

# JavaScript로 가림 요소 숨기기
def hide_overlay(driver):
    try:
        driver.execute_script("document.getElementById('modalDiv').style.display = 'none';")
        logger.info("Overlay hidden using JavaScript.")
    except Exception as e:
        logger.warning(f"Failed to hide overlay: {e}")

# 다운로드 버튼 클릭 및 파일 다운로드
def download_excel_file(driver, download_dir, xpath):
    logger.info(f"Attempting to download file using XPath: {xpath}")
    hide_overlay(driver)  # 가림 요소 숨기기
    # 다운로드 버튼이 클릭 가능할 때까지 대기 (최대 10초)
    download_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    download_button.click()
    wait_for_download_to_complete(download_dir, timeout=60)
    logger.info("File download initiated and completed.")
    return True

# 최근 다운로드 파일 찾기
def get_latest_downloaded_file(download_dir):
    time.sleep(3)
    list_of_files = glob.glob(os.path.join(download_dir, '*.xlsx'))
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        logger.info(f"Latest downloaded file found: {latest_file}")
        return latest_file
    logger.warning("No files found in the download directory.")
    return None

# # 엑셀 파일 읽어오기
# def read_excel_from_directory(download_dir):
#     latest_file = get_latest_downloaded_file(download_dir)
#     if latest_file and latest_file.endswith('.xlsx'):
#         new_excel_file = os.path.join(download_dir, 'hotel_list.xlsx')
#         os.rename(latest_file, new_excel_file)
#         df = pd.read_excel(new_excel_file, engine='openpyxl')
#         csv_file = os.path.join(download_dir, 'hotel_list.csv')
#         df.to_csv(csv_file, index=False, encoding='utf-8-sig')
#         logger.info(f"Excel file processed and saved as CSV: {csv_file}")
#         return df, new_excel_file, csv_file
#     logger.warning("No valid Excel file found in the directory.")
#     return None, None, None

# 엑셀 파일 읽어오기
def read_excel_from_directory(download_dir):
    latest_file = get_latest_downloaded_file(download_dir)
    if latest_file and latest_file.endswith('.xlsx'):
        # 파일 이름을 그대로 유지하면서 새로운 엑셀 파일 경로 설정
        new_excel_file = latest_file  # 파일 이름 변경 없음
        df = pd.read_excel(new_excel_file, engine='openpyxl')
        
        # CSV 파일 경로는 엑셀 파일과 같은 이름을 사용하되 확장자만 변경
        csv_file = os.path.splitext(new_excel_file)[0] + '.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        logger.info(f"Excel file processed and saved as CSV: {csv_file}")
        return df, new_excel_file, csv_file
    logger.warning("No valid Excel file found in the directory.")
    return None, None, None


# 데이터베이스에 저장
def save_to_db(df, engine):
    df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if 'NO' in df.columns:
        df = df.drop(columns=['NO'])
        
    with engine.connect() as connection:
        new_df = df
        new_df.to_sql('hotel_list', con=engine, if_exists='append', index=False)
        logger.info(f"{len(new_df)} rows of new data saved to MariaDB successfully.")

# 파일 삭제
def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"File {file_path} deleted.")
    else:
        logger.warning(f"File {file_path} does not exist.")

# 크롤링 및 DB 저장 함수
def crawl_and_save_to_db(download_dir):
    start_time = time.time()
    driver = setup_driver(download_dir)
    # 페이지 URL로 이동
    url = "https://www.hotelrating.or.kr/status_hotel_list.do"
    driver.get(url)
    logger.info(f"Accessed URL: {url}")
    webdriver
    # 첫 번째 버튼 (등급결정 호텔 리스트)
    download_excel_file(driver, download_dir, "//button[contains(@class, 'purple') and contains(text(), '등급결정 호텔 리스트')]")
    df, excel_file, csv_file = read_excel_from_directory(download_dir)
    if df is not None:
        engine = create_sqlalchemy_engine()
        save_to_db(df, engine)
        remove_file(excel_file)
        remove_file(csv_file)

    # 두 번째 버튼 (제주특별자치도관광협회 등급결정 호텔 리스트)
    download_excel_file(driver, download_dir, "//button[contains(@class, 'gray') and contains(text(), '제주특별자치도관광협회 등급결정 호텔 리스트')]")
    df, excel_file, csv_file = read_excel_from_directory(download_dir)
    if df is not None:
        engine = create_sqlalchemy_engine()
        save_to_db(df, engine)
        remove_file(excel_file)
        remove_file(csv_file)

    driver.quit()
    end_time = time.time()
    logger.info(f"Crawling and saving to DB completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    download_dir = '/home/ubuntu/hotel'  # 다운로드 폴더 경로 설정
    crawl_and_save_to_db(download_dir)
