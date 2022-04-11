import requests
from xml.etree.ElementTree import fromstring, parse
####한국어 형태소 분석기####
from konlpy.tag import Komoran

komoran = Komoran()

url = 'http://apis.data.go.kr/1741000/DisasterMsg3/getDisasterMsg1List'
params ={'serviceKey' : 'jPI0C9d3WB4hVbjtWVye1mYvAxDjIoC/Zu2HswIlVYUwxm8L2M0gZAyzMXCvLEWmaT8oI9r5WjLJaWhX3Eubag==', 'pageNo' : '1', 'numOfRows' : '2', 'type' : 'xml' }

# 공공api 서버 데이터 요청
response = requests.get(url, params=params)
xml = response.content.decode('utf-8')

tree = fromstring(xml)
rows = tree.findall("row")

for row in rows:
    newdict = dict()
    # xml 파싱 후 python dictionary로 변환
    newdict["create_date"] = row.findtext("create_date")
    newdict["location_id"] = row.findtext("location_id")
    newdict["location_name"] = row.findtext("location_name")
    newdict["md101_sn"] = row.findtext("md101_sn")
    newdict["msg"] = row.findtext("msg")
    newdict["send_platform"] = row.findtext("send_platform")

    keyword = komoran.nouns(newdict["msg"])
    print(keyword)


    
