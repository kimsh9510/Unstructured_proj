from pymongo import MongoClient

my_client = MongoClient("mongodb://localhost:27017/")
db = my_client.test
col_news = db.news
print(my_client.list_database_names())
