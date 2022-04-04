from pymongo import MongoClient

my_client = MongoClient("mongodb://localhost:27017/")   # DB 클라이언트 생성
db = my_client.test     # 데이터베이스 지정
col_news = db.news     # 콜렉션 지정
print(my_client.list_database_names())  # 데이터베이스 리스트 출력
