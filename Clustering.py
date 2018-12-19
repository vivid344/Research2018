import MySQLdb
import MeCab
import gensim
import os
import numpy as np
import LDA

def similar_cosign(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def get_vector_expression(id, news, lda, dict):
    vector = np.zeros(LDA.topic_N)
    m = MeCab.Tagger()
    keywords = m.parse(news)
    test_word_list = []
    test_word_lists = []
    for row in keywords.split('\n'):
        r = row.split('\t')
        word = r[0]
        if word == 'EOS':
            break
        else:
            pos = r[1].split(',')[0]
            if pos == '名詞':
                test_word_list.append(word)

    test_word_lists.append(test_word_list)
    test_corpus = [dict.doc2bow(text) for text in test_word_lists]

    for topics_per_document in lda[test_corpus]:
        for i in topics_per_document:
            vector[i[0]] = i[1]
    # print(vector)
    return vector


if __name__ == '__main__':
    connection = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd=os.environ['MYSQLPASS'],
                                 db='research', charset='utf8')
    select_sql = 'select id, body from News where id > 600'
    cursor1 = connection.cursor()
    cursor1.execute(select_sql)
    vectors = np.zeros(0)

    # 関連ファイルの読み込み
    lda = gensim.models.LdaModel.load('tmp/lda.model')
    dict = gensim.corpora.Dictionary.load('tmp/deerwester.dict')
    count = 0
    first_vector = None

    for row in cursor1:
        if count == 0:
            first_vector = get_vector_expression(row[0], row[1], lda, dict)
        elif count == 1:
            vectors = np.concatenate([[first_vector], [get_vector_expression(row[0], row[1], lda, dict)]])
        else:
            vectors = np.concatenate([vectors, [get_vector_expression(row[0], row[1], lda, dict)]])
        count += 1
    print(vectors)