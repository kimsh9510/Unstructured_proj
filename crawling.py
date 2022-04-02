from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time


def get_contents_from_news(soup, news):
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
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(5)
    full_html = driver.page_source
    soup = BeautifulSoup(full_html, "html.parser")
    contents = get_contents_from_news(soup, news)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(5)
    return contents.replace('\n', '').replace('\t', '').strip()


def get_location(cols):
    ret = ""
    for i in range(0, len(cols)):
        if cols[i].getText() == 'N/A':
            break
        if i != 0:
            ret += " "
        ret += cols[i].getText()

    return ret


def get_data(output="output.txt"):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    url = 'http://rscanner.ndmi.go.kr/scanning/damage_news2.php'
    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get(url=url)
    driver.implicitly_wait(5)

    full_html = driver.page_source
    soup = BeautifulSoup(full_html, "html.parser")
    table_body = soup.select_one('.dataTable > tbody')
    rows = table_body.select('tr')
    links = driver.find_elements(by=By.CSS_SELECTOR, value="table > tbody > tr > td > a")

    out = open(output, "w", encoding="utf-8")
    err_cnt = 0
    filter_type = ["도로교통재난사고", "사업장산재", "안전취약계층사고"]
    for i in range(0, len(rows)):
        try:
            row = rows[i]
            columns = row.select('td')
            disaster_type = columns[1].getText()
            if disaster_type in filter_type:
                continue
            location = get_location(columns[4:6])
            date = columns[7].getText()[0:10]
            news = columns[8].getText()
            title = columns[9].getText()
            links[i].click()
            time.sleep(2)
            contents = get_main_contents(driver, news)
            line = dict()
            line['유형'] = disaster_type
            line['위치'] = location
            line['날짜'] = date
            line['제목'] = title
            line['내용'] = contents
            out.write(str(line))
            out.write('\n')
        except Exception as error:
            print(error)
            err_cnt += 1

    print(err_cnt)
    out.close()
    driver.quit()
