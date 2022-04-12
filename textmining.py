from konlpy.tag import Okt
from database import col_news
from collections import Counter
import matplotlib.pyplot as plt


def show_graph(keyword_cnt):
    # 한글 폰트 설정
    plt.rc("font", family='AppleGothic')
    plt.rcParams['axes.unicode_minus'] = False

    plt.xlabel = "주요 키워드"
    plt.ylabel = "빈도수"
    plt.grid(True)

    # value와 key를 vaue값에 대한 내림차순으로 정렬
    sorted_values = sorted(keyword_cnt.values(), reverse=True)
    sorted_keys = sorted(keyword_cnt, key=keyword_cnt.get, reverse=True)

    # 막대 차트
    plt.bar(range(len(keyword_cnt)), sorted_values, align='center')
    plt.xticks(range(len(keyword_cnt)), list(sorted_keys), rotation="70")
    plt.show()

    # 파이 차트
    explode = [0.1 for i in range(len(keyword_cnt))]
    plt.pie(keyword_cnt.values(), labels=keyword_cnt.keys(), autopct='%.1f%%', explode=explode)
    plt.show()


def text_mining():
    okt = Okt()
    # 주요 키워드
    keywords = ["태풍", "홍수", "풍랑", "가뭄", "강풍", "해일",
                "산사태", "대설", "한파", "낙뢰", "폭염", "지진",
                "황사", "녹조", "적조", "조수", "자연우주물체",
                "화재", "산불", "폭발", "붕괴", "교통사고", "미세먼지",
                "감염병", "테러", "자살"]

    items = col_news.find()
    noun_list = list()
    # 형태소 분석기를 통해 텍스트 데이터에서 명사 추출
    for item in items:
        noun_list += okt.nouns(item['title'])
        noun_list += okt.nouns(item['contents'])

    keyword_cnt = dict()
    # 추출한 명사 중 주요 keyword의 개수를 count
    for noun in noun_list:
        if noun == '코로나':  # 코로나 단어는 감염병으로 포함하였다.
            noun = '감염병'
        if noun in keywords:
            if keyword_cnt.get(noun):
                keyword_cnt[noun] += 1
            else:
                keyword_cnt[noun] = 1

    # 전체 명사중 빈도수로 상위 50개의 명사를 구한다.
    most_word = dict()
    count = Counter(noun_list)
    for tags, counts in count.most_common(50):
        if len(str(tags)) > 1:
            most_word[tags] = counts

    show_graph(keyword_cnt)  # 주요 키워드에 대한 차트 출력
    # show_graph(most_word)  # 상위 50개 키워드에 대한 차트 출력


