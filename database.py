from pymongo import MongoClient

my_client = MongoClient("mongodb://localhost:27017/")
print(my_client.list_database_names())
