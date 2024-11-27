import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

# 크롤링 결과 저장 리스트
list1 = []

# 기본 시와 추가 단어 리스트를 사용하여 키워드 자동 생성
base_cities = ["김포", "부천", "시흥", "광명", "안산", "파주", "고양"]
additional_keywords = ["호텔", "컨벤션", "연수원"]

# 리스트 컴프리헨션을 사용하여 전체 키워드 생성
keywords = [f"{city} {word}" for city in base_cities for word in additional_keywords]

# 불용어 목록
stopwords = ["애완", "애견", "스테이", "청소년", "맥주", "학원", "베이커리", "골프", "LG", "KT", "여기어때", "고양이", "냥냥", "리무진", "수양관",
            "이마트", "BHC", "주차장", "은행", "교회", "학교", "테니스", "충전소", "올리브영", "카페", "레스토랑", "투어", "학생",
            "CU", "노래", "쏘카", "강아지", "펫", "클럽", "학과", "마음수련", "명상", "모텔", "태극권", "수련원", "세븐일레븐", "G car zone", 
            "정발산", "국선도", "안전교육", "ATM", "공무원교육원", "놀다가자", "워터스", "시티텔", "종합주택", "코자자", "이마트",
            "게스트하우스", "태극선", "이코노미", "침구", "펀비어킹", "토요코인", "병원", "슬립", "안내소", "문화센터", "정문", "후문", "식당",
            "휴식", "더휴식", "피티샵", "호텔얌", "호텔야", "투썸", "분양", "ICS", "레지던스", "스쿨",
            "본사", "하이테크", "케이크", "도시락", "호스텔", "PC", "런드리", "사무소", 
            "브라운도트", "스크린"]  # 여기에 제거할 장소명 또는 키워드를 추가

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 헤드리스 모드
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 크롬 드라이버 시작
driver = webdriver.Chrome(options=chrome_options)

def search_and_crawl(keyword, pbar):
    ind = 1  # 현재 복사한 순서
    no = 1  # 1~5페이지 중 위치한 곳
    page = 1  # 현재 페이지 번호
    
    # 카카오맵 검색 실행
    kakao_map_search_url = f"https://map.kakao.com/?q={keyword}"
    driver.get(kakao_map_search_url)
    time.sleep(1)  # 검색 후 잠시 대기
    driver.get(kakao_map_search_url)  # 문구가 덮이는 문제로 재시도
    time.sleep(1)  # 페이지 로딩 대기
    

    # 전체 장소 수 계산
    total_places = int(driver.find_elements(By.XPATH, '//*[@id="info.search.place.cnt"]')[0].text.replace(',', ''))
    places_per_page = 15

    # max_page와 마지막 장소 계산
    max_page = total_places // places_per_page + (1 if total_places % places_per_page > 0 else 0)
    last_page_places = total_places % places_per_page if total_places % places_per_page > 0 else places_per_page

    # 첫 페이지에서 장소의 개수 확인
    first_page_places = len(driver.find_elements(By.XPATH, '//*[@id="info.search.place.list"]/li'))
    if first_page_places >= 6:
        print(f"첫 페이지에 {first_page_places}개의 장소가 있습니다. 크롤링 후 더보기를 클릭합니다.")
        # 첫 페이지의 장소 크롤링 후 "더보기" 버튼 클릭
        crawl_places_on_page(keyword, page, first_page_places)  # 첫 페이지 크롤링
        click_more_button()  # 더보기 클릭
        time.sleep(1)
    else:
        print(f"첫 페이지에 {first_page_places}개의 장소가 있습니다. 바로 더보기를 클릭하고 크롤링을 시작합니다.")
        click_more_button()  # 더보기 클릭 후 크롤링 시작
        time.sleep(1)

    # 장소 수가 6개 이상이면 첫 페이지 크롤링 진행
    while page <= max_page:
        try:
            # 페이지 크롤링
            crawl_places_on_page(keyword, page, places_per_page if page < max_page else last_page_places)

            # 진행 상태 업데이트
            pbar.update(places_per_page if page < max_page else last_page_places)
            
            # 다음 페이지로 이동
            if page == max_page:
                break

            # 페이지 넘김 처리 (5페이지마다 다음 버튼 클릭)
            if no >= 5:
                click_next_button()
                no = 1  # 페이지 위치 초기화
            else:
                click_page_button(no + 1)
                no += 1

            page += 1

        except NoSuchElementException:
            break
def crawl_places_on_page(keyword, page, max_places):
    global ind
    for ind in range(1, max_places + 1):
        try:
            title = driver.find_element(By.XPATH, f'//*[@id="info.search.place.list"]/li[{ind}]/div[3]/strong/a[2]').text
            if any(word in title for word in stopwords):
                print(f"[제외] 불용어 포함: {title}")
                continue
            add = driver.find_element(By.XPATH, f'//*[@id="info.search.place.list"]/li[{ind}]/div[5]/div[2]/p[1]').text
            point = driver.find_elements(By.XPATH, f'//*[@id="info.search.place.list"]/li[{ind}]/div[4]/span[1]/em')[0].text
            try:
                homepage_button = driver.find_element(By.XPATH, f'//*[@id="info.search.place.list"]/li[{ind}]/div[5]/div[4]/a[2][@data-id="homepage"]')
                if homepage_button.is_displayed():
                    homepage_button.click()
                    time.sleep(1)
                    driver.switch_to.window(driver.window_handles[-1])
                    url = driver.current_url
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    url = None
            except NoSuchElementException:
                url = None
            
            list1.append([keyword, title, add, point, url])
            print(f"[크롤링 중] 키워드: {keyword}, 장소명: {title}, url: {url}")
            time.sleep(0.5)

        except NoSuchElementException:
            continue

def click_more_button():
    try:
        more_button = driver.find_element(By.XPATH, '//*[@id="info.search.place.more"]')
        if more_button.is_displayed():
            more_button.click()
            time.sleep(1)
    except NoSuchElementException:
        print("더보기 버튼을 찾지 못했습니다.")

def click_next_button():
    try:
        next_button = driver.find_element(By.XPATH, '//*[@id="info.search.page.next"]')
        if next_button.is_displayed():
            next_button.click()
            time.sleep(1)
    except NoSuchElementException:
        print("다음 버튼을 찾지 못했습니다.")

def click_page_button(page_no):
    try:
        page_button = driver.find_element(By.XPATH, f'//*[@id="info.search.page.no{page_no}"]')
        page_button.click()
        time.sleep(1)
    except NoSuchElementException:
        print(f"{page_no} 페이지 버튼을 찾지 못했습니다.")

# 각 키워드를 반복하여 검색 및 크롤링 실행
# 시작 시간 기록
start_time = time.time()

# 전체 크롤링 진행 상황을 표시할 경우:
places_per_page = 15
total_places_to_crawl = len(keywords) * places_per_page * 5 # 총 크롤링할 장소 수 // 평균 5개의 페이지가 있다고 가정
with tqdm(total=total_places_to_crawl, desc='전체 크롤링 진행 중', ncols=100) as pbar:
    for keyword in keywords:
        search_and_crawl(keyword, pbar)  # tqdm 객체를 파라미터로 전달

# 크롤링 결과를 데이터프레임으로 변환
df = pd.DataFrame(list1, columns=['keyword','title', 'address', 'point', 'url'])

# 불용어가 포함된 장소 제거
for word in stopwords:
    df = df[~df['title'].str.contains(word)]

# 결과를 CSV 파일로 저장
df.to_csv("kakao_crawled_fin.csv", index=False, encoding='utf-8-sig')

# 데이터프레임의 행 갯수 출력
print(f"총 {len(df)}개의 행이 있습니다.")

# 종료 시간 기록
end_time = time.time()

# 크롤링 소요 시간 출력
elapsed_time = end_time - start_time

print(f"크롤링 완료 및 CSV 저장 완료! 소요 시간: {elapsed_time:.2f}초")