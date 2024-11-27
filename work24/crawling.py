import mysql.connector
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.alert import Alert
import re
import time
from datetime import datetime, timedelta
import pandas as pd
import logging

# 기본 로거 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 파일 핸들러 설정
file_handler = logging.FileHandler('app.log', encoding='utf-8')  # UTF-8 인코딩 설정
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 핸들러 추가
logger.addHandler(file_handler)

# 현재 시간 출력 
now = datetime.now()
# 현재 시간을 출력하기
print("▶️▶️▶️▶️▶️▶️▶️▶️▶️▶️ 시작 시간 :", now, "◀️◀️◀️◀️◀️◀️◀️◀️◀️◀️")

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1231",
        database="crawling",
        port=3306,
        charset="utf8mb4",
        collation="utf8mb4_general_ci"
    )

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # 헤드리스 모드 추가
    options.add_argument("--no-sandbox")
    options.add_argument('--no-cache')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-popup-blocking")  # 팝업 차단 옵션
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    return driver

def scrape_data(driver, page_num):
    df = pd.DataFrame()
    date = get_today_minus_7_days()
    end_date = 99991231
    url = f'https://www.work24.go.kr/hr/a/a/1100/trnnCrsInf.do?dghtSe=A&traingMthCd=A&tracseTme=40&endDate=20250911&keyword1=&keyword2=&pageSize=10&orderBy=ASC&startDate_datepicker={date}&currentTab=1&topMenuYn=&pop=&tracseId=ACG20213000786518&pageRow=10&totamtSuptYn=A&crseTracseSeNum=&keywordType=1&gb=&keyword=&kDgtlYn=&area=00%7C%EC%A0%84%EA%B5%AD+%EC%A0%84%EC%B2%B4&orderKey=2&mberSe=&kdgLinkYn=&totTraingTime=A&crseTracseSe=A%7C%EC%A0%84%EC%B2%B4&tranRegister=&mberId=&i2=A&pageId=2&programMenuIdentification=EBG020000000310&endDate_datepicker={end_date}&monthGubun=&pageOrder=2ASC&pageIndex={page_num}&bgrlInstYn=&startDate={date}&ncs=&gvrnInstt=&selectNCSKeyword=&action=trnnCrsInfPost.do'
    driver.get(url)

    time.sleep(5)  # 페이지 시도 전 대기 시간

    for i in range(1, 11):
        try:
            # 새 창으로 전환하기 전에 메인 창의 핸들 저장
            main_window = driver.current_window_handle
            
            # Data Extraction
            type_xpath = f'//*[@id="tab-panel-02"]/div/div[2]/div[{i}]/div[2]/p[1]'
            type_element = driver.find_element(By.XPATH, type_xpath)
            type_ = re.sub(r'\n', ', ', type_element.text)
            time.sleep(5) 
            driver.find_element(By.XPATH, f'//*[@id="tab-panel-02"]/div/div[2]/div[{i}]/div[2]/h3/a').click()
            time.sleep(3)
            driver.switch_to.window(driver.window_handles[-1])
            
            # Scrape information
            company_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[1]/p').text
            title_ = re.sub(r'(모집마감|모집중)', '', driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[1]/h4').text).strip()
            total_cost_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[2]/dl/dd[1]/p').text
            cost_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[2]/dl/dd[1]/div/p').text
            percent_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[1]/div/div/span').text
            ALLscore_text = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[2]/span[2]/span').get_attribute("title")
            ALLscore_ = float(re.sub('[가-힣]','', re.search(r'기준(\d+(\.\d+)?)점', ALLscore_text).group()))
            NCS_job_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[3]/span[2]').text
            NCS_level_ = re.sub('[^0-9]','', driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[4]/span[2]').text)
            test_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[5]/span[2]').text.split()[0]
            certi_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[6]/span[2]').text
            date_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[7]/span[2]').text
            time_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[8]/span[2]').text
            old_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[9]/span[2]').text
            Pname_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[10]/span[2]').text
            Pphone_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[11]/span[2]').text
            Pmail_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[12]/span[2]').text
            depart_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[13]/span[2]').text
            train_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[14]/span[2]').text
            # 먼저 첫 번째 XPath에서 텍스트를 확인
            key_text = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[16]/span[1]').text

            # "주야구분/주말여부" 텍스트를 확인한 후 조건 분기
            if key_text == "주야구분/주말여부":
                # 주야구분/주말여부일 경우 li[16]/span[2]의 텍스트 추출
                night_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[16]/span[2]').text
            else:
                # 그렇지 않으면 li[17]/span[2]의 텍스트 추출
                night_ = driver.find_element(By.XPATH, '//*[@id="section1"]/div/div[2]/div[1]/div[2]/div/ul/li[17]/span[2]').text
            skill_ = driver.find_element(By.XPATH, '//*[@id="section1-1"]/div[2]/table/tbody').text

            # 후기 정보
            driver.find_element(By.XPATH, '//*[@id="infoTab4"]/button').click()
            time.sleep(1)
            result_elements_1 = driver.find_elements(By.CLASS_NAME, 'item')
            hoo_row = {}

            for result_score in result_elements_1:
                result_text = result_score.text
                key__ = result_text.split('\n')[0]
                key_ = re.sub(r'\((3|4|5)점\)', '', key__)

                # 첫 번째 형식인지 두 번째 형식인지 판별
                if len(result_text.split('\n')) > 1:
                    value__ = result_text.split('\n')[1]
                else:
                    value__ = result_text.split(' ')[-1]
                try:
                    if key_ != '추천합니다':
                        value_ = re.sub(r'[^0-9.]','',value__.split('\n')[1])
                    else:
                        value_ = value__.split('\n')[1]
                except:
                    value_ = value__
                # hoo_row에 key-value 저장
                hoo_row[f'{key_}'] = value_

            # 후기 내용
            try:
                try:
                    # 첫 번째 XPATH 시도
                    review_text = driver.find_element(By.XPATH, '//*[@id="section1-4"]/div[8]').text
                except:
                    # 첫 번째 XPATH가 없을 경우 두 번째 XPATH 시도
                    review_text = driver.find_element(By.XPATH, '//*[@id="section1-4"]/div[7]').text

                # 성공적으로 찾았을 경우 저장
                hoo_row['review'] = review_text
            except Exception as e:
                # 둘 다 없을 경우 except로 넘어감
                print(f"Error retrieving review: {e}")

            # 빈 값이 있는 항목 필터링(상세 만족도가 없는 경우 빈 딕셔너리를 생성함)
            hoo_row = {k: v for k, v in hoo_row.items() if k and v}
            # Create row
            row_ = {'company' : company_, 'title' : title_,  'total_cost' : total_cost_, 'cost_' : cost_, 
                    'job_acceptance_rate' : percent_, 'average_score' : ALLscore_, 'NCS_classification' : NCS_job_,
                    'NCS_level' : NCS_level_, 'NCS_application_status' : test_, 'certifications' : certi_, 'training_duration' : date_,
                    'training_time' : time_, 'average_age' : old_, 'Pname' : Pname_, 'Pphone' : Pphone_,
                    'Pmail' : Pmail_, 'depart' : depart_, 'train' : train_, 'day_night_weekend' : night_, 
                    'training_goal' : skill_, 'train_type' : type_}
            row_.update(hoo_row)

            df = pd.concat([df, pd.DataFrame([row_])], ignore_index=True)
            df.reset_index(drop=True, inplace=True)
        except Exception as e:
            print(f"Error occurred: {e}")
        # 수정된 코드
        finally:
            try:
                # 현재 창이 메인 창이 아닌 경우에만 닫기
                if driver.current_window_handle != main_window:
                    driver.close()
                    time.sleep(2)
                    driver.switch_to.window(main_window)
            except Exception as e:
                logger.error(f"Error in window handling: {str(e)}")
                # 모든 핸들이 닫혔을 경우 드라이버 재시작
                if len(driver.window_handles) == 0:
                    driver = setup_driver()
            
    return df

def save_to_db(df, cursor, connection):
    column_mapping = {
        '평균만족도': 'average_satisfaction',
        '수강인원': 'number_of_students',
        '평가인원': 'number_of_evaluators',
        '평가참가율': 'evaluation_participation_rate',
        'review': 'review',
        '추천합니다': 'recommend',
        '전반적 만족도': 'overall_satisfaction',
        '경력개발지원': 'career_development_support',
        '과제 및 피드백': 'assignments_and_feedback',
        '교강사': 'instructors',
        '훈련과정 편성 및 운영': 'training_program_planning_and_operation',
        '훈련과정 현장지향성': 'training_program_field_orientation',
        '훈련환경 및 장비': 'training_environment_and_equipment',
        '훈련환경': 'training_environment',
        '능력향상': 'skill_improvement',
        '목표달성': 'goal_achievement',
        '수강가치': 'value_of_training',
        '프로젝트 학습': 'project_based_learning',
        '훈련과정 실무연계성': 'training_program_practical_connection',
        '훈련내용': 'training_content',
        '훈련교사': 'training_instructors',
        '훈련방법': 'training_method',
        '시설장비': 'facilities_and_equipment',
        '행정서비스': 'administrative_services',
        '취업지원': 'employment_support',
        '훈련수준': 'training_level',
        '학습지원': 'training_support',        
        '훈련성취도': 'training_achievement',
        '취업가능성': 'employment_possibility',
        '평가 및 피드백' : 'test_and_feedback',
        '경력개발지원 및 학생관리' : 'Career_Development_Support_and_Student_Management',
        '고용가능성' : 'employability'
    }
    
    df.rename(columns=column_mapping, inplace=True)
    df = df.fillna('-')
    
    columns = df.columns.tolist()
    insert_query = f"""
        INSERT IGNORE INTO work24_data ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    
    for i, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))
    connection.commit()

# 팝업 닫기 함수
def close_alert(driver):
    try:
        alert = Alert(driver)
        alert.dismiss()  # 팝업을 닫음
        logging.info("팝업이 닫혔습니다.")
    except NoAlertPresentException:
        logging.info("팝업이 존재하지 않습니다.")

def get_today_minus_7_days():
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    return seven_days_ago.strftime('%Y%m%d')  # 'YYYYMMDD' 형식으로 반환

def main():
    connection = connect_to_db()
    cursor = connection.cursor()
    driver = setup_driver()
    start_time = datetime.now()
    # 자동화를 위한 날짜 지정
    date = get_today_minus_7_days()
    page_num = 1
    # date = 20230101
    end_date = 99991231
    url = f'https://www.work24.go.kr/hr/a/a/1100/trnnCrsInf.do?dghtSe=A&traingMthCd=A&tracseTme=40&endDate=20250911&keyword1=&keyword2=&pageSize=10&orderBy=ASC&startDate_datepicker={date}&currentTab=1&topMenuYn=&pop=&tracseId=ACG20213000786518&pageRow=10&totamtSuptYn=A&crseTracseSeNum=&keywordType=1&gb=&keyword=&kDgtlYn=&area=00%7C%EC%A0%84%EA%B5%AD+%EC%A0%84%EC%B2%B4&orderKey=2&mberSe=&kdgLinkYn=&totTraingTime=A&crseTracseSe=A%7C%EC%A0%84%EC%B2%B4&tranRegister=&mberId=&i2=A&pageId=2&programMenuIdentification=EBG020000000310&endDate_datepicker={end_date}&monthGubun=&pageOrder=2ASC&pageIndex={page_num}&bgrlInstYn=&startDate={date}&ncs=&gvrnInstt=&selectNCSKeyword=&action=trnnCrsInfPost.do'
    driver.get(url) 
    
    total_pages_text = driver.find_element(By.XPATH, '//*[@id="searchForm"]/div[3]/ul/li[1]/button/span').text
    # 정규식을 사용하여 숫자와 천 단위 구분 기호를 포함한 페이지 수 추출
    total_pages_num = re.search(r'\d+(?:,\d+)*', total_pages_text).group()
        
    # 천 단위 구분 기호를 제거하여 정수로 변환
    total_pages_num = int(total_pages_num.replace(',', ''))
    # 숫자로 변환 (int 형으로 변환)
    total_pages = int(total_pages_num / 10)
    
    driver.close()
    driver = setup_driver()
    
    pages_completed = 0
    elapsed_times = []
    
    try:

        logging.info(f"크롤링 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"총 페이지 공고 개수: {total_pages} 중 {total_pages - page_num} 남음!")

        while page_num <= total_pages:
            try:
                logging.info(f"페이지 {page_num} 시작")

                page_start_time = datetime.now()
                df = scrape_data(driver, page_num)
                page_end_time = datetime.now()
                page_elapsed_time = page_end_time - page_start_time
                elapsed_times.append(page_elapsed_time.total_seconds())

                if df.empty:
                    logging.info(f"페이지 {page_num}에 데이터가 없습니다. 종료합니다.")
                    break

                save_to_db(df, cursor, connection)
                logging.info(f"페이지 {page_num} 데이터베이스에 저장 완료")

                pages_completed += 1
                average_time_per_page = sum(elapsed_times) / len(elapsed_times)
                remaining_pages = total_pages - pages_completed
                estimated_remaining_time = average_time_per_page * remaining_pages
                estimated_remaining_minutes = estimated_remaining_time / 60

                logging.info(f"페이지 {page_num} 종료")
                logging.info(f"현재까지 완료된 페이지 수: {pages_completed}")
                logging.info(f"평균 소요 시간(초): {average_time_per_page:.2f}")
                logging.info(f"남은 페이지 수: {total_pages - page_num}")
                logging.info(f"추정 남은 시간(분): {estimated_remaining_minutes:.2f}")

                page_num += 1

            except UnexpectedAlertPresentException as e:
                logging.error(f"Unexpected alert detected on page {page_num}: {str(e)}")
                close_alert(driver)  # 팝업을 닫음
                time.sleep(5)  # 5초 대기 후 다시 시도

    finally:
        driver.quit()
        cursor.close()
        connection.close()
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        logging.info(f"크롤링 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"총 소요 시간: {elapsed_time}")

if __name__ == "__main__":
    main()