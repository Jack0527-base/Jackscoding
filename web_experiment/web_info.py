import csv
from bs4 import BeautifulSoup

base_url = 'D:\\Jack\\Python\\web_experiment\\douban.html'

all_data = []

for page in range(1, 11):  # 修改为1到10页
    file_path = base_url.format(page)
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'lxml')
    movie_list = soup.find('ol', class_='grid_view').find_all('li')

    for movie in movie_list:
        # 获取电影名称
        title = movie.find('div', class_='hd').find('span', class_='title').get_text()

        # 获取评价分数
        rating_num = movie.find('div', class_='bd').find('div').find(
            'span', class_='rating_num'
        ).get_text()

        # 获取评论人数
        comment_num = movie.find('div', class_='bd').find('div').find_all(
            'span'
        )[-1].get_text().strip('人评价')

        # 导演和主演信息
        directors_info = movie.find('div', class_='bd').find('p').get_text().strip().split('\n')[0].strip()
        directors_part = directors_info.split('导演: ')[1]

        if '主演: ' in directors_info:
            actors = directors_part.split('主演: ')[1].strip()
        else:
            actors = ''

        directors = directors_part.split('主演: ')[0].strip()

        # 上映时间、出品地、剧情类别
        info = movie.find('div', class_='bd').find('p').get_text().strip().split('\n')[1].strip()
        year = info.split('/')[0].strip()
        country = info.split('/')[1].strip()
        category = info.split('/')[2].strip()

        # 电影标题图链接
        pic = movie.find('div', class_='item').find('div', class_='pic').find(
            'a'
        ).find('img').get('src')

        # 将所有信息存为一行
        row = [
            title, rating_num, comment_num,
            directors, actors, year, country, category, pic
        ]

        all_data.append(row)

# 确保只提取最多250部电影的信息
all_data = all_data[:250]

# 将所有数据保存到 CSV 文件中
output_file_path = 'douban_top250.csv'  # 使用原始文件名
try:
    with open(output_file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)

        # 写入表头
        writer.writerow([
            '电影名称', '评价分数', '评论人数',
            '导演', '主演', '上映时间',
            '出品地', '剧情类别', '电影标题图链接'
        ])


        # 写入数据
        writer.writerows(all_data)

    print(f'数据抽取完成，已保存到 {output_file_path} 文件中。')
except PermissionError:
    print(f"无法写入文件 {output_file_path}，请确保文件未被占用并且你有足够的权限。")


