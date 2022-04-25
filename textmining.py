from konlpy.tag import Kkma, Okt
from database import col_news
from collections import Counter
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize
import numpy as np
from gensim.models.word2vec import Word2Vec
from pprint import pprint

kkma = Kkma()
okt = Okt()


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


def text2sentences(text):   # 텍스트를 문장 단위로 나눔
    sentences = kkma.sentences(text)
    for i in range(0, len(sentences)):
        if len(sentences[i]) <= 10:     # 길이가 10 이하인 문장은 앞의 문장과 합친다.
            sentences[i - 1] += (' ' + sentences[i])
            sentences[i] = ''
    return sentences


def get_nouns(sentences, stopwords):    # 단어에서 명사 추출
    okt = Okt()
    nouns = []
    for sentence in sentences:
        if sentence is not '':
            nouns.append(' '.join([noun for noun in okt.nouns(str(sentence))
                                   if noun not in stopwords and len(noun) > 1]))    # 불용어 제외, 길이 1 단어 제외
    return nouns    # 명사로 이루어진 문장 반환


def build_sentence_graph(sentence):  # TF-IDF sentence graph 생성
    tfidf = TfidfVectorizer()
    tfidf_mat = tfidf.fit_transform(sentence).toarray()
    graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
    return graph_sentence


def build_words_graph(sentence):   # TF-IDF word graph 생성
    cnt_vec = CountVectorizer()
    cnt_vec_mat = normalize(cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
    vocab = cnt_vec.vocabulary_
    return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word]: word for word in vocab}


def get_ranks(graph, d=0.85):   # TextRank 값 계산
    A = graph
    matrix_size = A.shape[0]
    for id in range(matrix_size):
        A[id, id] = 0
        link_sum = np.sum(A[:, id])
        if link_sum != 0:
            A[:, id] /= link_sum
        A[:, id] *= -d
        A[id, id] = 1

    B = (1 - d) * np.ones((matrix_size, 1))
    ranks = np.linalg.solve(A, B)
    return {idx: r[0] for idx, r in enumerate(ranks)}


def summarize(sentences, sorted_sent_rank_idx, cnt=3):  # TextRank 값 상위 cnt개의 문장을 출력
    index = []
    for idx in sorted_sent_rank_idx[:cnt]:
        index.append(idx)
    index.sort()

    for idx in index:
        pprint(sentences[idx])


def get_keywords(idx2word, sorted_word_rank_idx, cnt=10):
    keywords = []
    index = []
    for idx in sorted_word_rank_idx[:cnt]:
        index.append(idx)

    for idx in index:
        keywords.append(idx2word[idx])

    print(keywords)


def text_mining():
    # 주요 키워드
    keywords = ["태풍", "홍수", "풍랑", "가뭄", "강풍", "해일",
                "산사태", "대설", "한파", "낙뢰", "폭염", "지진",
                "황사", "녹조", "적조", "조수", "자연우주물체",
                "화재", "산불", "폭발", "붕괴", "교통사고", "미세먼지",
                "감염병", "테러", "자살"]

    # 불용어
    stopwords = ['곳', '수', '고', '그', '명', '층', '것', '전',
                 '이', '및', '등', '나', '알', '위해', '재', '씨',
                 '며', '각', '동영상', '화질', '재생', '입력', '크게'
                 '표준', '컨트롤', '안내', '고정', '취소']

    items = col_news.find()
    noun_list = list()
    # 형태소 분석기를 통해 텍스트 데이터에서 명사 추출
    for item in items:
        # noun_list.append([word for word in okt.nouns(item['title']) if word not in stopwords])
        # noun_list.append([word for word in okt.nouns(item['contents']) if word not in stopwords])

        # 텍스트 문장 단위로 추출
        sentences = text2sentences(item['contents'])
        sentences.append(item['title'])
        # 문장에서 단어 추출
        nouns = get_nouns(sentences, stopwords)
        if not nouns:
            continue
        # TF-IDF 모델, 그래프 생성
        sent_graph = build_sentence_graph(nouns)
        words_graph, idx2word = build_words_graph(nouns)
        # TextRank 계산
        sent_rank_idx = get_ranks(sent_graph)   # 문장 간 text rank 계산
        sorted_sent_rank_idx = sorted(sent_rank_idx, key=lambda k: sent_rank_idx[k], reverse=True)  # 점수 큰 값 부터 인덱스 나열
        word_rank_idx = get_ranks(words_graph)  # 단어 간 text rank 계산
        sorted_word_rank_idx = sorted(word_rank_idx, key=lambda k: word_rank_idx[k], reverse=True)  # 점수 큰 값 부터 인덱스 나열
        # 뉴스 기사 본문 요약 문장 출력
        summarize(sentences, sorted_sent_rank_idx)
        # 뉴스 기사 핵심 키워드 출력
        get_keywords(idx2word, sorted_word_rank_idx)

    # print(noun_list)
    # model = Word2Vec(sentences=noun_list, vector_size=100, window=5, min_count=5, workers=4, sg=0)
    # print(model.wv.vectors.shape)
    # print(model.wv.most_similar('산불'))

    # keyword_cnt = dict()
    # 추출한 명사 중 주요 keyword의 개수를 count
    # for noun in noun_list:
    #     if noun == '코로나':  # 코로나 단어는 감염병으로 포함하였다.
    #         noun = '감염병'
    #     if noun in keywords:
    #         if keyword_cnt.get(noun):
    #             keyword_cnt[noun] += 1
    #         else:
    #             keyword_cnt[noun] = 1
    #
    # # 전체 명사중 빈도수로 상위 50개의 명사를 구한다.
    # most_word = dict()
    # count = Counter(noun_list)
    # for tags, counts in count.most_common(50):
    #     if len(str(tags)) > 1:
    #         most_word[tags] = counts

    # show_graph(keyword_cnt)  # 주요 키워드에 대한 차트 출력
    # show_graph(most_word)  # 상위 50개 키워드에 대한 차트 출력


