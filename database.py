from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URL = os.environ.get('MONGO_URL')     # mongodb://user:password@host:port
client = MongoClient(MONGO_URL)   # DB 클라이언트 생성
db = client.종프1     # 데이터베이스 지정
col_msg = db.재난문자
col_news = db.news     # 콜렉션 지정
print(client.list_database_names())  # 데이터베이스 리스트 출력
