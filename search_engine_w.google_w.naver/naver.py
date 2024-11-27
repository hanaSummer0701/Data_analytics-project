from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
from datetime import datetime

# 날짜 조건 설정
start_date = datetime.strptime("2024.01.01", "%Y.%m.%d")
end_date = datetime.strptime("2024.07.31", "%Y.%m.%d")

keywords = ['기획자 과정', '2개월 교육과정', '취업지원교육', '3개월 교육과정', '단기 교육과정',  '취업연계과정', '서울시 교육']
options = Options()
options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)
# save list
all_results = []

stopwords = ['국기 ', 'KDT', 'K-digital training', '나무위키','지식백과', '위키백과']

# keywords
for keyword in keywords:
    # page
    for page_num in range(2, 11):
        start = (page_num -2) * 15 + 1
        url = f'https://search.naver.com/search.naver?nso=&page={page_num}&query={keyword}&sm=tab_pge&start={start}&where=web'
        driver.get(url)
        # data
        for i in range(1, 16):
            try:
                try: 
                    title = driver.find_element(By.XPATH, f'//*[@id="main_pack"]/section[1]/div/ul/li[{i}]/div/div[2]/div[2]/a').text
                    if '더보기' in title:
                        title = driver.find_element(By.XPATH, f'//*[@id="main_pack"]/section/div/ul/li[{i}]/div[1]/div[2]/div[1]/a').text
                except:   
                    title = driver.find_element(By.XPATH, f'//*[@id="main_pack"]/section/div/ul/li[{i}]/div[1]/div[2]/div[1]/a').text
                # 날짜를 가져오는 부분
                try:
                    date = driver.find_element(By.XPATH, f'//*[@id="main_pack"]/section[1]/div/ul/li[{i}]/div/div[2]/div[3]/a/span/span').text
                except: 
                    try:
                        date = driver.find_element(By.XPATH, f'//*[@id="main_pack"]/section/div/ul/li[{i}]/div/div[2]/div[2]/a/span/span').text
                    except:
                        date = '-'  # 두 번째 XPath도 실패할 경우 '-'로 설정
                try:       
                    url = driver.find_element(By.XPATH, f'//*[@id="main_pack"]/section[1]/div/ul/li[{i}]/div/div[2]/div[2]/a').get_attribute('href')
                except:
                    url = driver.find_element(By.XPATH, f'//*[@id="main_pack"]/section/div/ul/li[{i}]/div/div[2]/div[1]/a').get_attribute('href')
                    
                name = driver.find_element(By.XPATH, f'//*[@id="main_pack"]/section[1]/div/ul/li[{i}]/div/div[1]/div/div[2]/a[2]/span[1]').text
                if 'tistory' in name:
                    name = 'tistory'
                # Check for stopwords in both name and title
                if any(word in name for word in stopwords) or any(word in title for word in stopwords):
                    print(f"[제외] 불용어 포함: name - {name}")
                    continue       
                
               # 날짜 끝의 '.' 제거
                if date.endswith('.'):
                    date = date[:-1]
                
                # 날짜에 "주 전" 또는 "일 전" 포함 여부 체크
                if '주 전' in date or '일 전' in date:
                    print(f"[제외] 날짜 조건에 불합격: {date}")
                    continue 
                
                # Check date validity
                if date != '-':
                    date_obj = datetime.strptime(date, "%Y.%m.%d")
                    if date_obj < start_date or date_obj > end_date:
                        print(f"[제외] 날짜 조건에 불합격: {date}")
                        continue
                    
                # save data
                all_results.append({
                    'keyword' : keyword,
                    'name' : name,
                    'title' : title,
                    'date' : date,
                    'url' : url
                })
            except Exception as e:
                print(f"error {i} on page{page_num} for keyword '{keyword}' : {e}")
        print(f'========={page_num} page complete !=========')
        time.sleep(2)
    print(f'>>>>>>>>>{keyword} complete !>>>>>>>>>')
    
df = pd.DataFrame(all_results)

driver.close()

df.to_excel('naver_without_KDT_data.xlsx')