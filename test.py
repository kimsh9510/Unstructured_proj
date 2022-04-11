####한국어 형태소 분석기####
from konlpy.tag import Kkma, Komoran, Okt, Hannanum

okt = Okt()
kkma = Kkma()
komoran = Komoran()
hannanum = Hannanum()
# To extract only noun in text data

keyword = komoran.nouns("안녕하세요, 헤이 테크 블로그의 자연어처리 관련 포스팅입니다. 1234-!5123 @!@!@@$")
print(keyword)