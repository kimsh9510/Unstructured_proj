import concurrent
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, Keys
from pymongo import MongoClient

#크롤링시 firefox사용

def db_write(news_tittle, news_time, news_contents): #DB입력 함수
    host = "localhost"
    port = "27017"
    mongo = MongoClient(host, int(port))
    db = mongo.test
    col = db.yna_news
    dict_list = list()
    for i in range(0, len(news_tittle)): #dictionary 배열로 변환
        dictionary = dict()
        dictionary['tittle'] = news_tittle[i]
        dictionary['time'] = news_time[i]
        dictionary['contents'] = news_contents[i]
        dict_list.append(dictionary)
    col.insert_many(dict_list)
    return


def go_to_start_page(driver: webdriver, start_page):  # 시작할 페이지로 이동
    page_section = driver.find_element(by=By.CSS_SELECTOR, value='div.paging')
    present_page = int(page_section.find_element(by=By.CSS_SELECTOR, value='strong').text)
    page_pointer = int(start_page)

    if present_page == page_pointer:
        pass
    else:
        next_button_num = page_pointer // 10
        page_remainder = page_pointer % 10
        for i in range(0, next_button_num):
            next_button = driver.find_element(by=By.CSS_SELECTOR, value='.nextPage')
            next_button.click()
        page_section = driver.find_element(by=By.CSS_SELECTOR, value='div.paging')
        page_remainder_button = page_section.find_elements(by=By.CSS_SELECTOR, value='a')[page_remainder - 1]
        page_remainder_button.click()
    return


def move_to_next_page(driver: webdriver, present_page):  # 다음 페이지로 이동
    page_section = driver.find_element(by=By.CSS_SELECTOR, value='div.paging')
    if present_page // 10 == 0:
        if present_page % 10 == 0:
            next_button = driver.find_element(by=By.CSS_SELECTOR, value='.nextPage')
            next_button.click()
            present_page = present_page + 1
        else:
            page_button = page_section.find_elements(by=By.CSS_SELECTOR, value='a')[(present_page % 10) - 1]
            page_button.click()
            present_page = present_page + 1
    else:
        if present_page % 10 == 0:
            next_button = driver.find_element(by=By.CSS_SELECTOR, value='.nextPage')
            next_button.click()
            present_page = present_page + 1
        else:
            page_button = page_section.find_elements(by=By.CSS_SELECTOR, value='a')[present_page % 10]
            page_button.click()
            present_page = present_page + 1
    return present_page


def get_data(start_page, last_page):  # 각 페이지별 크롤링
    tittle = list() #제목
    contents = list() #내용
    news_time = list() #시간

    driver = webdriver.Firefox()  # 이 파일의 같은 위치에 geckodriver 필요
    driver.implicitly_wait(3)

    url = 'https://www.yna.co.kr/safe/news' #연합뉴스 재난 포털 최신뉴스
    driver.get(url)

    html = driver.page_source
    go_to_start_page(driver, start_page) # 시작 페이지로 이동
    present_page = start_page
    news_list = driver.find_elements(by=By.CSS_SELECTOR, value='.headline-zone > ul > li')
    for t in range(0, (last_page - start_page)):
        for i in range(0, len(news_list)):
            temp = news_list[i].text
            temp_split = temp.split('\n')
            news_time.append(temp_split[0])
            tittle.append(temp_split[1])

            link_list_len = len(driver.find_elements(by=By.CSS_SELECTOR, value='.headline-zone > ul > li > article'))
        for i in range(0, link_list_len):
            link_list = driver.find_elements(by=By.CSS_SELECTOR, value='article')
            link = link_list[i].find_element(by=By.CSS_SELECTOR, value='div > h3')
            driver.find_element(by=By.CSS_SELECTOR, value='html').send_keys(Keys.PAGE_DOWN)
            link.click()
            time.sleep(0.5)
            contents_list = driver.find_elements(by=By.CSS_SELECTOR, value='.story-news > p')
            temp_str = ''
            for j in range(0, len(contents_list)):
                temp_str = temp_str + ' ' + contents_list[j].text
            contents.insert(i, temp_str)
            driver.back()
            time.sleep(0.5)
        if present_page != last_page:
            present_page = move_to_next_page(driver, present_page)
            news_list = driver.find_elements(by=By.CSS_SELECTOR, value='.headline-zone > ul > li')
        else:
            pass
    db_write(tittle, news_time, contents) #DB입력
    return

