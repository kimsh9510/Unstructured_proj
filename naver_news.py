from multiprocessing import freeze_support
from bs4 import BeautifulSoup
import requests
from newspaper import Article
from pymongo import MongoClient
from fake_useragent import UserAgent
from multiprocessing import Pool
from datetime import datetime, timedelta
from newspaper import Config

def check_lastpage(serch, page, year1, year2, month1, month2, day1, day2): # 마지막 페이지를 확인하는 함수
    url = makeUrl(serch, page, year1, year2, month1, month2, day1, day2)
    ua = UserAgent()
    header = {'user-agent': ua.random}
    r = requests.request("GET", url, headers=header)
    html = BeautifulSoup(r.text, "html.parser")
    page_next_button = html.select_one('#main_pack > div.api_sc_page_wrap > div > a.btn_next')
    while True:
        if page_next_button is not None and "aria-disabled" in page_next_button.attrs:
            page_attrs = page_next_button.attrs["aria-disabled"]
            break
        else:
            url = makeUrl(serch, page, year1, year2, month1, month2, day1, day2)
            ua = UserAgent()
            header = {'user-agent': ua.random}
            r = requests.request("GET", url, headers=header)
            html = BeautifulSoup(r.text, "html.parser")
            page_next_button = html.select_one('#main_pack > div.api_sc_page_wrap > div > a.btn_next')
    if page_attrs == "true":
        return False
    else:
        return True


def db_write(news_tittle, news_time, news_contents):  # DB입력 함수
    host = "localhost"
    port = "27017"
    mongo = MongoClient(host, int(port))
    db = mongo.test
    col = db.naver_news
    dict_list = list()
    for i in range(0, len(news_tittle)):  # dictionary 배열로 변환
        for j in range(0, len(news_tittle[i])):
            dictionary = dict()
            dictionary['tittle'] = news_tittle[i][j]
            dictionary['time'] = news_time[i][j]
            dictionary['contents'] = news_contents[i][j]
            dict_list.append(dictionary)
            col.insert_one(dictionary)
    return


def makePgNum(num):
    if num == 1:
        return num
    elif num == 0:
        return num + 1
    else:
        return num + 9 * (num - 1)


# 크롤링할 url 생성하는 함수 만들기(검색어, 페이지, 기간의 날짜들((1의 날짜들부터 2의 날짜들 까지))
def makeUrl(search, pg, y1, y2, m1, m2, d1, d2):
    page = makePgNum(pg)
    if len(str(m1)) < 2:
        m1 = str(0)+str(m1)
    else:
        pass
    if len(str(d1)) < 2:
        d1 = str(0)+str(d1)
    else:
        pass
    if len(str(m2)) < 2:
        m2 = str(0)+str(m2)
    else:
        pass
    if len(str(d2)) < 2:
        d2 = str(0)+str(d2)
    else:
        pass
    url = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=' + search + '&sort=0&photo=0&field=0&pd=3&ds='+ str(y1) +'.'+ str(m1) +'.'+ str(d1) +'&de='+ str(y2) +'.'+ str(m2) +'.'+ str(d2) +'&cluster_rank=24&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:from'+ str(y1) + str(m1) + str(d1) +'to'+ str(y2) + str(m2) + str(d2)  +',a:all&start=' + str(page)
    return url


def get_data(naver_url): #각 페이지에 접근하여 그 페이지의 기사들을 크롤링 하는 함수
    ua = UserAgent()
    header = {'user-agent': ua.random}
    r_naver = requests.request("GET", naver_url, headers=header)
    naver_html = BeautifulSoup(r_naver.text, "html.parser")
    articles = naver_html.select("div.group_news > ul.list_news > li div.news_area > a")
    articles_url = list()
    articles_tittle = list()
    articles_contents = list()
    articles_date = list()
    try:
        for i in range(0, len(articles)):
            articles_url.append(articles[i].attrs['href'])
        for t in range(0, len(articles_url)):
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
            config = Config()
            config.browser_user_agent = user_agent
            config.request_timeout = 101
            article = Article(articles_url[t], language='ko', config=config, headers=header)
            article.download()
            article.parse()
            articles_tittle.append(article.title)
            articles_contents.append(article.text)
            articles_date.append(article.publish_date)
        return articles_tittle, articles_url, articles_contents, articles_date
    except Exception as error:
        print(error)
        return articles_tittle, articles_url, articles_contents, articles_date


def start(url):
    news_titles = list()
    news_url = list()
    news_contents = list()
    news_date = list()
    temp_tittle, temp_url, temp_content, temp_date = get_data(url)
    news_titles.append(temp_tittle)
    news_url.append(temp_url)
    news_contents.append(temp_content)
    news_date.append(temp_date)
    db_write(news_titles, news_date, news_contents)
    return


def multi_processing_crawling(): #멀티프로세싱
    # 검색어 입력
    search = input("검색할 키워드를 입력해주세요:")
    how_many = int(input("검색할 기간을 입력해주세요 ex)730 -> 오늘부터 2년치를 검색 : "))
    term = int(input("몇일 단위로 검색할지 입력해주세요 ex) 7 -> 7일 단위로 2년 검색 :")) #단위가 크면 누락된 날이 많아진다.
    page = 1
    urls = list()
    check = True
    time1 = datetime.now()
    for i in range(0, (how_many // term)): # 마지막 페이지 체크 및 url 배열 만들기
        time2 = time1 + timedelta(days=-term)
        while check:
            check = check_lastpage(search, page, time2.year, time1.year, time2.month, time1.month, time2.day, time1.day)
            page += 1
        check = True
        for j in range(1, page):
            urls.append(makeUrl(search, j, time2.year, time1.year, time2.month, time1.month, time2.day, time1.day))
        time1 = time2 + timedelta(days=-1)
        page = 1

    pool = Pool(processes=8)  # 8개의 프로세스를 사용합니다.
    pool.map(start, urls)  # pool에 일을 던져줍니다
    pool.close()
    pool.join()
    return


if __name__ == '__main__':
    freeze_support()
    multi_processing_crawling()
