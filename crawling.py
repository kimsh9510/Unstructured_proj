from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from database import col_news
import time


def get_contents_from_news(soup, news):
    # 뉴스 종류에 따라 기사 내용이 있는 element에서 contents 수집
    selector = None
    if news == 'KBS':
        selector = '#cont_newstext'
    elif news == 'MBC':
        selector = 'div.news_txt'
    elif news == 'SBS':
        selector = 'div.text_area'
    elif news == 'YTN':
        selector = 'div.article > span'
    elif news == '강원일보':
        selector = 'knews_body'
    elif news == '경남도민일보':
        selector = 'article-view-content-div'
    elif news == '경북일보':
        selector = '#article-view-content-div'
    elif news == '광주일보':
        selector = '#joinskmbox'
    elif news == '국민일보':
        selector = 'div.tx'
    elif news == '대전일보':
        selector = '#CmAdContent > div#fontSzArea'
    elif news == '매일신문':
        selector = '#articlebody'
    elif news == '머니투데이':
        selector = '#textBody'
    elif news == '부산일보':
        selector = '.article_content'
    elif news == '서울경제':
        selector = '.article_view'
    elif news == '서울신문':
        selector = '.S20_v_article'
    elif news == '세계일보':
        selector = '.viewBox2'
    elif news == '한겨례':
        selector = '.text'
    elif news == '한국경제':
        selector = '#articletxt'
    elif news == '한국일보':
        selector = '.col-main'

    if selector is None:
        return ""
    else:
        return soup.select_one(selector).getText()


def get_main_contents(driver, news):
    driver.switch_to.window(driver.window_handles[-1])  # 새 탭으로 이동
    time.sleep(3)
    full_html = driver.page_source
    soup = BeautifulSoup(full_html, "html.parser")
    contents = get_contents_from_news(soup, news)   # 기사 내용 크롤링
    driver.close()  # 현재 탭 닫기
    driver.switch_to.window(driver.window_handles[0])   # 이전 탭으로 이동
    time.sleep(3)
    return contents.replace('\n', '').replace('\t', '').strip()     # 문자열 전처리


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

    full_html = driver.page_source
    soup = BeautifulSoup(full_html, "html.parser")
    table_body = soup.select_one('.dataTable > tbody')
    rows = table_body.select('tr')  # table 각각의 row 배열
    links = driver.find_elements(by=By.CSS_SELECTOR, value="table > tbody > tr > td > a")   # title 링크 배열

    err_cnt = 0
    filter_type = ["도로교통재난사고", "사업장산재", "안전취약계층사고", "자살"]   # filtering type
    result = list()
    for i in range(0, len(rows)):
        try:
            row = rows[i]
            columns = row.select('td')
            disaster_type = columns[1].getText()
            if disaster_type in filter_type:    # 재난 유형을 filtering
                continue
            location = get_location(columns[4:6])   # location 문자열을 합친다.
            date = columns[7].getText()[0:10]   # 날짜 뒤의 (None) 제거하여 저장
            news = columns[8].getText()
            title = columns[9].getText()
            links[i].click()   # 현재 기사의 링크 클릭
            time.sleep(3)
            contents = get_main_contents(driver, news)     # 기사의 내용을 가져온다.
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

    col_news.insert_many(result)    # db collection에 크롤링한 데이터 삽입
    print(err_cnt)
    driver.quit()
