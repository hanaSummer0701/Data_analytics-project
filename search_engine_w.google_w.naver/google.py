import logging
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re

# # 로깅 설정 (로그 파일 생성)
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger()

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # 로그 레벨 설정

# 로그 파일 핸들러 설정 (UTF-8 인코딩)
file_handler = logging.FileHandler(filename='google_crawler.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# 검색 키워드 리스트
keywords = ['기획자 과정', '2개월 교육과정', '취업지원교육', '3개월 교육과정', '단기 교육과정',
            '취업연계과정', '국비교육', 'KDT', '서울시 교육']

# 제외할 단어 목록
stopwords = ['천재', '새싹', 'sessac', '나무위키', '지식백과', '위키백과', 'youtube', 'lguplus', 'namu.wiki', 'homeplus', 'zocbo']

# 크롤링 날짜 설정
start_date = '1/1/2024'
end_date = '7/31/2024'

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# 결과를 저장할 리스트
all_results = []

# 현재 키워드의 인덱스 설정
current_keyword_index = 0 

while current_keyword_index < len(keywords):
    keyword = keywords[current_keyword_index]
    page_num = 0  # 각 키워드마다 페이지 번호를 초기화
    logger.info(f"키워드 '{keyword}'에 대한 크롤링을 시작합니다.")
    
    while True:
        # Google 검색 URL 구성
        google_url = f'https://www.google.com/search?q={keyword}&sca_esv=bcb030b5e9f56fd4&udm=14&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}&start={page_num * 10}'
        
        # 웹 드라이버 실행
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(google_url)
        time.sleep(2)

        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = soup.find_all('div', class_='g')  # 검색 결과 항목을 포함하는 div

            # 검색 결과가 없는 경우
            if not results:
                logger.info(f"키워드 '{keyword}'의 검색 결과가 없습니다. 다음 키워드로 넘어갑니다.")
                driver.quit()
                break  # 현재 키워드를 끝내고 다음 키워드로 이동

            # 검색 결과가 있는 경우 크롤링 수행
            for result in results:
                try:
                    time.sleep(1)
                    name = result.find('span', class_='VuuXrf')
                    name_text = name.text if name else "No name available"

                    title = result.find('h3', class_='LC20lb MBeuO DKV0Md')
                    title_text = title.text if title else "No title available"

                    date = result.find('span', class_='LEwnzc Sqrs4e')
                    date_text = date.text.strip().replace(' — ', '')
                    date_text = re.sub(r'\s*—\s*$', '', date_text) if date else "No date available"

                    # URL 추출
                    try:
                        url_text = result.find('div', class_='yuRUbf').find('a')['href'] 
                    except (TypeError, AttributeError):    
                        url_text = "No url available"

                    # if result.find('div', class_='yuRUbf').find('a')['href']:
                    #     url_text = 
                    #     url = result.find('cite', class_='qLRx3b tjvcx GvPZzd cHaqb')
                    # elif result.find('cite', class_='qLRx3b tjvcx GvPZzd dTxz9 cHaqb'):
                    #     url = result.find('cite', class_='qLRx3b tjvcx GvPZzd dTxz9 cHaqb')
                    # else:
                    #     url = None
                    # url_text = url.text.split(' ')[0] if url else "No URL available"

                    # stopwords에 포함된 단어가 제목이나 URL에 포함되지 않은 경우에만 저장
                    if not any(stopword in title_text for stopword in stopwords) and not any(stopword in url_text for stopword in stopwords):
                        all_results.append({
                            'keyword': keyword,
                            'name': name_text,
                            'title': title_text,
                            'date': date_text,
                            'url': url_text
                        })
                        logger.info(f"크롤링된 데이터 - 키워드:{keyword}, 이름: {name_text}, 제목: {title_text}, 날짜: {date_text}, URL: {url_text}")
                    else:
                        if any(stopword in title_text for stopword in stopwords):
                            logger.info(f"제목 '{title_text}'가 stopwords에 포함된 단어와 일치하여 제외되었습니다.")
                        elif any(stopword in url_text for stopword in stopwords):
                            logger.info(f"URL '{url_text}'가 stopwords에 포함된 단어와 일치하여 제외되었습니다.")

                except Exception as e:
                    logger.error(f"항목 처리 중 오류 발생: {e}")

            # 다음 페이지 버튼을 찾아 클릭
            try:
                next_button = driver.find_element(By.XPATH, '//*[@id="pnnext"]')
                next_button.click()
                time.sleep(3)  # 페이지가 로드될 시간을 기다림
                page_num += 1  # 다음 페이지로 이동
                time.sleep(1)
            except NoSuchElementException:
                logger.info(f"키워드 '{keyword}'에 대한 모든 페이지를 크롤링했습니다.")
                break  # 다음 페이지가 없으면 현재 키워드를 종료하고 다음 키워드로 이동

        except Exception as e:
            logger.error(f"페이지 처리 중 오류 발생: {e}")
            break
        
        finally:
            driver.quit()  # 정상 또는 오류 발생 시 항상 드라이버를 종료

    current_keyword_index += 1  # 현재 키워드를 완료했으므로 다음 키워드로 이동

logger.info(f"모든 키워드에 대한 크롤링을 완료했습니다. 총 {len(all_results)}개의 결과가 수집되었습니다.")

# 크롤링된 결과를 데이터프레임으로 변환 후 CSV 저장
results_df = pd.DataFrame(all_results)
results_df.to_csv('crawled_results.csv', index=False, encoding='utf-8-sig')
logger.info(f"'crawled_results.csv'에 결과가 저장되었습니다.")
