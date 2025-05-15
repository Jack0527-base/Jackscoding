import re
from flask import Flask, render_template, request, redirect, url_for, session
from peewee import MySQLDatabase, Model, CharField, FloatField, IntegerField, AutoField

# 配置数据库
db = MySQLDatabase(
    "douban_top250",
    host="localhost",
    port=3306,
    user="root",
    password="06z05r27B",
    charset='utf8mb4'
)

# 定义 Peewee 模型
class Movie(Model):
    id = AutoField()
    title = CharField()
    rating_num = FloatField()
    comment_num = IntegerField()
    directors = CharField()
    actors = CharField()
    year = CharField()
    country = CharField()
    category = CharField()
    pic = CharField()

    class Meta:
        database = db
        table_name = 'douban_movie'

# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 必须设置 session 密钥

# 首页
@app.route('/')
def home():
    return render_template('home.html')

# 登录页面（GET）
@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('form.html')

# 登录处理（POST）
@app.route('/signin', methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return render_template('form.html', message='用户名和密码不能为空', username=username or '')

    if username == 'Jack' and password == 'password':
        session['logged_in'] = True
        session['username'] = username
        return render_template('signin-ok.html', username=username)

    return render_template('form.html', message='用户名或密码错误', username=username)

# 退出登录
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# 搜索页面（登录后可访问）
@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    if not session.get('logged_in'):
        return redirect(url_for('signin_form'))

    if request.method == 'POST':
        year = request.form.get('year')
        if not re.fullmatch(r'^\d{4}$', year):
            return render_template('search_movie.html', error="请输入4位数字年份")

        movies = Movie.select().where(Movie.year == year)
        return render_template('search_result.html', movies=movies, year=year)

    return render_template('search_movie.html')

# 启动应用
if __name__ == '__main__':
    db.connect()
    app.run(debug=True)
