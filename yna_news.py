from multiprocessing import Pool
from multiprocessing import Process, freeze_support
from bs4 import BeautifulSoup
import requests
from requests import request
import time
from pymongo import MongoClient


# 크롤링시 firefox사용

def db_write(news_tittle, news_time, news_contents):  # DB입력 함수
    host = "localhost"
    port = "27017"
    mongo = MongoClient(host, int(port))
    db = mongo.test
    col = db.yna_news
    dict_list = list()
    for i in range(0, len(news_tittle)):  # dictionary 배열로 변환
        dictionary = dict()
        dictionary['tittle'] = news_tittle[i]
        dictionary['time'] = news_time[i]
        dictionary['contents'] = news_contents[i]
        dict_list.append(dictionary)
    col.insert_many(dict_list)
    return


def get_page_link(url, start_page, present_page):  # 각 페이지 url 생성
    page_link_list = list()
    for i in range(start_page, present_page + 1):
        page_link = url + '/' + str(i)
        page_link_list.append(page_link)
    return page_link_list


def get_data(url):  # 각 페이지별 크롤링
    tittle = list()  # 제목
    contents = list()  # 내용
    news_time = list()  # 시간
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
              "Accept-Encoding": "*",
              "Connection": "keep-alive"}
    r = requests.request("GET", url, headers=header)
    html = BeautifulSoup(r.text, "html.parser")
    news_list = html.select('.headline-zone > ul > li')
    for i in range(0, len(news_list)):
        tittle.append(news_list[i].select_one('article > div > h3 > a').text)
        news_time.append(news_list[i].select_one('span').text)

    link_list = html.select('.headline-zone > ul > li > article > div > h3 > a')
    for i in link_list:
        link = i.attrs['href']
        link = 'http:' + link
        r_news = request("GET", link, headers=header)
        news_html = BeautifulSoup(r_news.text, "html.parser")
        contents_list = news_html.select('#articleWrap > div > p')
        temp_str = ''
        for j in range(0, len(contents_list)):
            temp_str = temp_str + ' ' + contents_list[j].text
        contents.append(temp_str)
    db_write(tittle, news_time, contents)  # DB입력
    return


def multi_processing_crawling_choose():  # 페이지 선택 가능
    page1 = input("시작 페이지:")
    page2 = input("마지막 페이지:")
    pool = Pool(processes=8)  # 8개의 프로세스를 사용합니다.
    pool.map(get_data, get_page_link('https://www.yna.co.kr/safe/news', int(page1), int(page2)))
    pool.close()
    pool.join()
    return


start = time.time()
if __name__ == '__main__':
    freeze_support()
    multi_processing_crawling_choose()  # or multi_processing_crawling_all
    multi_processing_crawling_choose()
    multi_processing_crawling_choose()
    multi_processing_crawling_choose()
    multi_processing_crawling_choose() #오류 발생으로 인해 나누어서 실행하였다.

end = time.time()

print(str(end - start))
