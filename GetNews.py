# Yahooニュースから情報を取得してきて，DBに格納する
# テスト段階のスクレイピングのため，Yahooニュースの主要上位100件を取得してくる．
# DBはDockerで起動したmysql URL:http://127.0.0.1:3306 User:root Pass:????

import requests
import io
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import MySQLdb
from time import sleep
import os


category = [
    '国内',
    '国際',
    '経済',
    'エンタメ',
    'スポーツ',
    'IT・科学',
    'ライフ',
    '地域'
]

category_id = [
    'gnPridomestic',
    'gnPriinternational',
    'gnPribusiness',
    'gnPrientertainment',
    'gnPrisports',
    'gnPritechnology',
    'gnPrilife',
    'gnPrilocal'
]


class MyHtmlStripper(HTMLParser):
    def __init__(self, s):
        super().__init__()
        self.sio = io.StringIO()
        self.feed(s)

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        self.sio.write(data)

    @property
    def value(self):
        return self.sio.getvalue()


# Yahooのニュースサイトから本文を取得する
def get_news_text(url):
    response_base = requests.get(url)
    response_base.encoding = 'UTF-8'
    response_bs = BeautifulSoup(response_base.content, 'lxml')
    news_text_area = response_bs.find('p', {'ynDetailText yjDirectSLinkTarget'})
    return MyHtmlStripper(str(news_text_area)).value


# YahooのニュースサイトからタイトルとURLを取得する
def get_news_data():
    base_url = 'https://news.yahoo.co.jp/list/?p='

    # とりあえず最新の10P分 rangeの値で取得件数を変更できる
    for i in range(1, 3):
        response_base = requests.get(base_url + str(i))
        response_base.encoding = 'UTF-8'
        response_bs = BeautifulSoup(response_base.content, 'lxml')

        # ニュースが書かれているエリアのみ抽出
        news_area = response_bs.find('div', {'listArea'})

        # ニュース部分(20件)をリストで取得
        news_lists = news_area.findAll('li', {'ListBoxwrap'})

        for news in news_lists:
            # 各データを取得
            sleep(1)
            news_tmp_url = news.find('a').get('href')
            news_img = news.find('img').get('data-src')
            news_title = news.find('dt').string
            response_news_p1 = requests.get(news_tmp_url)
            response_news_p1.encoding = 'UTF-8'
            response_news_p1_bs = BeautifulSoup(response_news_p1.content, 'lxml')

            news_category_area = response_news_p1_bs.find('div', {'gnSecWrap'})
            news_category_id = news_category_area.find('li', {'current'}).get('id')

            news_category = category[category_id.index(news_category_id)]

            news_text_url = response_news_p1_bs.find('a', {'newsLink'}).get('href')
            news_text = get_news_text(news_text_url).replace('\n', '').replace(' ', '').replace('　', '')
            print(news_text)

            cursor = connection.cursor()

            insert_sql = "insert into News(url, title, body, category, image) value(%s, %s, %s, %s, %s)"
            cursor.execute(insert_sql, (news_text_url, news_title, news_text, news_category, news_img))
            connection.commit()
            cursor.close()


if __name__ == '__main__':
    connection = MySQLdb.connect(host='127.0.0.1', port=3306, user='root', passwd=os.environ['MYSQLPASS'],
                                 db='research', charset='utf8')
    get_news_data()
    connection.close()

