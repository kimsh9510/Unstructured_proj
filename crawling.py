from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from database import col_news
import time
from newspaper import Article


def get_location(cols):
    ret = ""
    for i in range(0, len(cols)):
        if cols[i].getText() == 'N/A':  # 더 이상 정보가 없다면 break
            break
        if i != 0:  # 첫번째 인덱스가 아니라면 공백 추가
            ret += " "
        ret += cols[i].getText()

    return ret


def get_data():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument('--blink-settings=imagesEnabled=false')

    url = 'http://rscanner.ndmi.go.kr/scanning/damage_news2.php'
    driver = webdriver.Chrome('chromedriver', options=options)  # chrome driver setting with options
    driver.get(url=url)     # url에 해당하는 사이트를 open
    driver.implicitly_wait(5)
    paginate_buttons = driver.find_elements(by=By.CSS_SELECTOR, value='#example_paginate > span > a')  # 페이지네이션

    err_cnt = 0
    result = list()

    start = time.time()  # 시간 측정 시작
    for i in range(0, len(paginate_buttons)):
        current_page = paginate_buttons[i]
        current_page.click()  # ith page로 이동
        full_html = driver.page_source  # 현재 page의 page source를 추출
        soup = BeautifulSoup(full_html, "html.parser")
        table_body = soup.select_one('.dataTable > tbody')
        rows = table_body.select('tr')  # table 각각의 row 배열
        links = table_body.select("tr > td > a")  # 뉴스 링크 배열
        for j in range(0, len(rows)):
            try:
                row = rows[j]
                columns = row.select('td')
                disaster_type = columns[1].getText()   # 재난 유형
                location = get_location(columns[4:6])   # location 문자열을 합친다.
                date = columns[7].getText()[0:10]   # 날짜 뒤의 (None) 제거하여 저장
                link = links[j].get('href')   # 기사 url
                article = Article(link, language="ko")
                article.download()
                article.parse()
                title = article.title  # 기사의 제목을 가져 온다.
                contents = article.text.replace('\n', '').replace('\t', '').strip()  # 기사의 내용을 가져 온다.
                line = dict()
                line['type'] = disaster_type
                line['location'] = location
                line['date'] = date
                line['title'] = title
                line['contents'] = contents
                result.append(line)       # dictionary 생성하여 배열에 삽입
            except Exception as error:
                print(error)    # error 발생시 출력하고 err의 개수를 1 증가시킨다.
                err_cnt += 1

    end = time.time()  # 시간 측정 완료
    print(f"크롤링 소요 시간: {end - start:.5f} sec")  # 소요 시간 출력
    col_news.insert_many(result)    # db collection에 크롤링한 데이터 삽입
    print(err_cnt)
    driver.quit()
