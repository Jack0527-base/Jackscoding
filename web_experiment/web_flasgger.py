from flask import Flask, request, session, redirect, url_for, render_template, jsonify
from peewee import MySQLDatabase, Model, CharField, FloatField, IntegerField, AutoField
from flasgger import Swagger
import re

# 配置数据库
db = MySQLDatabase(
    "douban_top250",
    host="localhost",
    port=3306,
    user="root",
    password="06z05r27B",
    charset='utf8mb4'
)

# 定义模型
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

# 初始化应用
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 配置 Swagger，设置访问地址为 /apidocs/
swagger = Swagger(app, config={
    "swagger_ui": True,
    "specs_route": "/apidocs/"
})

# 首页
@app.route('/')
def home():
    return render_template('home.html')

# 登录页面
@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('form.html')

# 登录
@app.route('/signin', methods=['POST'])
def signin():
    """
    用户登录
    ---
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: 登录成功或失败页面
    """
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
    """
    退出登录
    ---
    responses:
      302:
        description: 成功后跳转到首页
    """
    session.clear()
    return redirect(url_for('home'))

# 搜索页面
@app.route('/search', methods=['GET', 'POST'])
def search_movie():
    """
    按年份搜索电影
    ---
    parameters:
      - name: year
        in: formData
        type: string
        required: true
        description: 年份，4位数字
    responses:
      200:
        description: 返回符合年份的电影
    """
    if not session.get('logged_in'):
        return redirect(url_for('signin_form'))

    if request.method == 'POST':
        year = request.form.get('year')
        if not re.fullmatch(r'^\d{4}$', year):
            return render_template('search_movie.html', error="请输入4位数字年份")

        movies = Movie.select().where(Movie.year == year)
        return render_template('search_result.html', movies=movies, year=year)

    return render_template('search_movie.html')

# 启动
if __name__ == '__main__':
    db.connect()
    app.run(debug=True)
