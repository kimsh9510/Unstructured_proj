import requests
from pymongo import MongoClient
from pymongo.cursor import CursorType
from xml.etree.ElementTree import fromstring, parse

# MongoDB를 다루는 핸들러 클래스 선언
class DBHandler:
    def __init__(self):
        host = "localhost"
        port = "27017"
        self.client = MongoClient(host, int(port))

    def insert_item_one(self, data, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].insert_one(data).inserted_id
        return result

    def insert_item_many(self, datas, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].insert_many(datas).inserted_ids
        return result

    def find_item_one(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find_one(condition, {"_id": False})
        return result

    def find_item(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find(condition, {"_id": False}, no_cursor_timeout=True, cursor_type=CursorType.EXHAUST)
        return result

    def delete_item_one(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].delete_one(condition)
        return result

    def delete_item_many(self, condition=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].delete_many(condition)
        return result

    def update_item_one(self, condition=None, update_value=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].update_one(filter=condition, update=update_value)
        return result

    def update_item_many(self, condition=None, update_value=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].update_many(filter=condition, update=update_value)
        return result

    def text_search(self, text=None, db_name=None, collection_name=None):
        result = self.client[db_name][collection_name].find({"$text": {"$search": text}})
        return result

url = 'http://apis.data.go.kr/1741000/DisasterMsg3/getDisasterMsg1List'
params ={'serviceKey' : 'jPI0C9d3WB4hVbjtWVye1mYvAxDjIoC/Zu2HswIlVYUwxm8L2M0gZAyzMXCvLEWmaT8oI9r5WjLJaWhX3Eubag==', 'pageNo' : '1', 'numOfRows' : '2', 'type' : 'xml' }

# 공공api 서버 데이터 요청
response = requests.get(url, params=params)
xml = response.content.decode('utf-8')

tree = fromstring(xml)
rows = tree.findall("row")

# 객체 생성
mongo = DBHandler()

for row in rows:
    newdict = dict()
    # xml 파싱 후 python dictionary로 변환
    newdict["create_date"] = row.findtext("create_date")
    newdict["location_id"] = row.findtext("location_id")
    newdict["location_name"] = row.findtext("location_name")
    newdict["md101_sn"] = row.findtext("md101_sn")
    newdict["msg"] = row.findtext("msg")
    newdict["send_platform"] = row.findtext("send_platform")

    print(newdict)

    # 기존의 DB에 동일한 데이터가 존재하는지 확인
    compare_dict = mongo.find_item_one({"create_date": newdict["create_date"]}, "종프1", "재난문자")

    if compare_dict is None:
        # 동일한 데이터가 없으면 데이터 Insert
        # 종프1 database에 재난문자 collection에 Insert
        mongo.insert_item_one(newdict, "종프1", "재난문자")
    
