from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver import ActionChains, Keys
from pprint import pprint
from pymongo import MongoClient
from pymongo.cursor import CursorType


def db_write(news_tittle, news_time, contents):
    host = "localhost"
    port = "27017"
    mongo = MongoClient(host, int(port))
    db = mongo.test
    dictionary = {'tittle': news_tittle[i] for i in range(len(news_tittle))}
    db.test.insert_many(dictionary)


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
    tittle = list()
    contents = list()
    news_time = list()

    driver = webdriver.Firefox()  # 이 파일의 같은 위치에 chromedriver 필요
    driver.implicitly_wait(3)

    url = 'https://www.yna.co.kr/safe/news'
    driver.get(url)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    temp_list = list()
    go_to_start_page(driver, start_page)
    present_page = start_page
    news_list = driver.find_elements(by=By.CSS_SELECTOR, value='ul.list > li')
    for t in range(0, (last_page - start_page)):
        for i in range(0, len(news_list) - 8):
            temp = news_list[i].text
            temp_split = temp.split('\n')
            news_time.append(temp_split[0])
            tittle.append(temp_split[1])

        link_list_len = len(driver.find_elements(by=By.CSS_SELECTOR, value='article'))
        print(str(link_list_len))
        for i in range(0, (link_list_len - 5)):
            link_list = driver.find_elements(by=By.CSS_SELECTOR, value='article')
            link = link_list[i].find_element(by=By.CSS_SELECTOR, value='div > h3')
            print(link.text)
            driver.find_element(by=By.CSS_SELECTOR, value='html').send_keys(Keys.PAGE_DOWN)
            link.click()
            time.sleep(0.5)
            contents_list = driver.find_elements(by=By.CSS_SELECTOR, value='.story-news > p')
            for j in range(0, len(contents_list)):
                temp_str = contents_list[j].text
                temp_list.append(temp_str)
            contents.insert(i, temp_list)
            driver.back()
            time.sleep(0.5)
        if present_page != last_page:
            present_page = move_to_next_page(driver, present_page)
            news_list = driver.find_elements(by=By.CSS_SELECTOR, value='ul.list > li')
        else:
            pass

    for i in range(0, len(news_time)):
        print("제목 : " + tittle[i])
        print("시간 : " + news_time[i])
        pprint(contents[i])

    return


