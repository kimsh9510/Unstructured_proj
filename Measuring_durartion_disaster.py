import requests
from pymongo import MongoClient
from pymongo.cursor import CursorType
from xml.etree.ElementTree import fromstring
from collections import deque
import pprint
import datetime

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

mongo = DBHandler()

def average_texting_time(disaster):
    query = {'msg' : {'$regex' : ".*" + disaster +".*"}}

    # i=0
    cnt=0
    denom=0
    prev_date = 0
    prev_location_id=0

    for item in mongo.client["종프1"]["재난문자"].find(query, {"_id": False}, cursor_type=CursorType.EXHAUST).sort('location_id') :
        # pprint.pprint(item)
        cnt+=1
        denom+=1
        
        time_data = item['create_date'][0:10]
        format_data = "%Y/%m/%d"
        date = datetime.datetime.strptime(time_data, format_data)

        if item['location_id'] == prev_location_id :
            if date == prev_date :
                cnt-=1
                denom-=1
            elif date + datetime.timedelta(days=1) == prev_date :
                denom-=1

        prev_date = date
        prev_location_id = item['location_id']

        # i+=1
        # if i == 20 :
        #     break

    # print(disaster, cnt, denom, cnt/denom)
    print(disaster, ":", cnt/denom)

disasters = ["태풍", "홍수", "가뭄", "강풍", "해일","산사태", "대설", "한파", "폭염", "지진",
"황사", "화재", "산불", "붕괴", "교통사고", "미세먼지", "감염병", "코로나", "확진"]

for disaster in disasters : 
    average_texting_time(disaster)