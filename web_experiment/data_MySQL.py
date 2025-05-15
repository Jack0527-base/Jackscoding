from bs4 import BeautifulSoup
from peewee import *
import os

# 数据库连接
db = MySQLDatabase("douban_top250", host="localhost", port=3306, user="root", passwd="06z05r27B", charset="utf8mb4")

# 表结构定义
class Movie(Model):
    title = CharField(max_length=200)
    rating_num = FloatField()
    comment_num = IntegerField()
    directors = CharField(max_length=200)
    actors = CharField(max_length=200)
    year = CharField(max_length=10)
    country = CharField(max_length=100)
    category = CharField(max_length=100)
    pic = CharField(max_length=200)

    class Meta:
        database = db
        table_name = 'douban_movie'


# 数据解析函数
def parse_movie_info(movie):
    title = movie.find('div', class_='hd').find('span', class_='title').get_text(strip=True)

    rating_num = float(movie.find('span', class_='rating_num').get_text(strip=True))

    # 取最后一个 span 获取评论人数
    comment_span = movie.find('div', class_='bd').find('div').find_all('span')[-1]
    comment_num = int(comment_span.get_text(strip=True).replace('人评价', '').replace(',', ''))

    p_tags = movie.find('div', class_='bd').find_all('p')
    info_lines = p_tags[0].get_text(strip=True, separator='\n').split('\n')

    directors = ''
    actors = ''
    if len(info_lines) >= 1:
        if '导演:' in info_lines[0]:
            parts = info_lines[0].split('导演: ')[1]
            if '主演: ' in parts:
                directors, actors = parts.split('主演: ')
            else:
                directors = parts.strip()

    # 第二行信息：年份 / 国家 / 类型
    year, country, category = '', '', ''
    if len(info_lines) >= 2:
        parts = info_lines[1].split('/')
        if len(parts) == 3:
            year = parts[0].strip()
            country = parts[1].strip()
            category = parts[2].strip()

    pic = movie.find('img').get('src')

    return {
        'title': title,
        'rating_num': rating_num,
        'comment_num': comment_num,
        'directors': directors.strip(),
        'actors': actors.strip(),
        'year': year,
        'country': country,
        'category': category,
        'pic': pic
    }


# 主函数
def main():
    db.connect()
    db.create_tables([Movie], safe=True)

    with open(r'D:\Jack\Python\web_experiment\douban.html', 'r', encoding='utf-8') as f:
        html = f.read()

    page_sections = html.split('<ol class="grid_view">')[1:]

    movies_to_insert = []

    for section in page_sections:
        section_html = '<ol class="grid_view">' + section
        soup = BeautifulSoup(section_html, 'lxml')
        movie_list = soup.find('ol', class_='grid_view').find_all('li')
        for movie in movie_list:
            try:
                info = parse_movie_info(movie)
                movies_to_insert.append(info)
            except Exception as e:
                print(f"解析失败，跳过该条记录: {e}")

    # 批量插入数据库
    with db.atomic():
        for i in range(0, len(movies_to_insert), 50):  # 每次插入50条
            Movie.insert_many(movies_to_insert[i:i + 50]).execute()

    db.close()
    print("数据提取并成功保存到数据库。")

if __name__ == '__main__':
    main()
