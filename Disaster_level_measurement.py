#-*- coding:utf-8 -*-
import requests
from pymongo import MongoClient
from pymongo.cursor import CursorType
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

# 객체 생성
mongo = DBHandler()

#{"msg": {"$regex" : ""}}
#{"create_date" : "2022/04/09 14:10:26"}
#{'location_id': {"$regex" : "104"}}
#{'create_date' : {$lt : '2022/04/09', $gt : '2022/04/01'}}
#{"msg": {"$not":{"$regex" : "확진"}}}


nowdate = datetime.datetime.strptime("2022/04/02 14:44", "%Y/%m/%d %H:%M")
nowdate_7 = nowdate - datetime.timedelta(days=7)
nowdate_7 = nowdate_7.strftime("%Y/%m/%d")
print(nowdate_7)

query = {'create_date' : {'$lt' : '2022/04/09', '$gt' : '2022/04/01 18:00:00'}}

local = dict()
disaster_list = ["확진", "건조"]
disaster_dict = {disaster : 0 for disaster in disaster_list}

for item in mongo.find_item(query, "종프1", "재난문자") :
    if item['location_name'] not in local :
        local[item['location_name']] =  disaster_dict.copy()

    for disaster in disaster_list:
        if disaster in item['msg']:
            local[item['location_name']][disaster] += 1  

    # pprint.pprint(item)

pprint.pprint(local)

