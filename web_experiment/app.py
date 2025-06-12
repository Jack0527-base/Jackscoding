"""
豆瓣电影Flask Web应用
"""
import re
from flask import Flask, render_template, request, redirect, url_for, session
from flasgger import Swagger

from config import FLASK_CONFIG
from models import Movie, User, connect_database, close_database


def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 应用配置
    app.secret_key = FLASK_CONFIG['secret_key']
    
    # 配置Swagger API文档
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    
    swagger = Swagger(app, config=swagger_config)
    
    return app


app = create_app()


# 用户认证装饰器
def login_required(f):
    """登录验证装饰器"""
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('signin_form'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@app.route('/')
def home():
    """
    首页
    ---
    tags:
      - 页面
    responses:
      200:
        description: 返回首页
    """
    return render_template('home.html')


@app.route('/signin', methods=['GET'])
def signin_form():
    """
    显示登录页面
    ---
    tags:
      - 用户认证
    responses:
      200:
        description: 返回登录页面
    """
    return render_template('form.html')


@app.route('/signin', methods=['POST'])
def signin():
    """
    用户登录处理
    ---
    tags:
      - 用户认证
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: 用户名
      - name: password
        in: formData
        type: string
        required: true
        description: 密码
    responses:
      200:
        description: 登录结果页面
      302:
        description: 重定向到首页或其他页面
    """
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    # 输入验证
    if not username or not password:
        return render_template('form.html', 
                             message='用户名和密码不能为空', 
                             username=username)

    # 连接数据库进行用户认证
    if not connect_database():
        return render_template('form.html', 
                             message='数据库连接失败，请稍后重试', 
                             username=username)
    
    try:
        # 确保用户表存在
        User.create_table_if_not_exists()
        
        # 用户认证
        user = User.authenticate(username, password)
        
        if user:
            session['logged_in'] = True
            session['username'] = user.username
            session['user_id'] = user.id
            return render_template('signin-ok.html', username=user.username)
        else:
            return render_template('form.html', 
                                 message='用户名或密码错误', 
                                 username=username)
    
    except Exception as e:
        print(f"登录过程中出错: {e}")
        return render_template('form.html', 
                             message='登录失败，请稍后重试', 
                             username=username)
    finally:
        close_database()


@app.route('/logout')
def logout():
    """
    退出登录
    ---
    tags:
      - 用户认证
    responses:
      302:
        description: 重定向到首页
    """
    session.clear()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册
    ---
    tags:
      - 用户认证
    parameters:
      - name: username
        in: formData
        type: string
        required: true
        description: 用户名
      - name: password
        in: formData
        type: string
        required: true
        description: 密码
      - name: confirm_password
        in: formData
        type: string
        required: true
        description: 确认密码
      - name: email
        in: formData
        type: string
        required: false
        description: 邮箱地址
    responses:
      200:
        description: 注册页面或结果
      302:
        description: 注册成功后重定向到登录页
    """
    if request.method == 'GET':
        return render_template('register.html')
    
    # 获取表单数据
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    email = request.form.get('email', '').strip() or None
    
    # 输入验证
    if not username or not password or not confirm_password:
        return render_template('register.html', 
                             message='用户名和密码为必填字段', 
                             username=username, email=email)
    
    if password != confirm_password:
        return render_template('register.html', 
                             message='两次输入的密码不一致', 
                             username=username, email=email)
    
    # 用户名和密码验证
    if len(username) < 3 or len(username) > 20:
        return render_template('register.html', 
                             message='用户名长度应在3-20个字符之间', 
                             username=username, email=email)
    
    if len(password) < 6 or len(password) > 20:
        return render_template('register.html', 
                             message='密码长度应在6-20个字符之间', 
                             username=username, email=email)
    
    # 用户名只能包含字母、数字和下划线
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return render_template('register.html', 
                             message='用户名只能包含字母、数字和下划线', 
                             username=username, email=email)
    
    # 邮箱格式验证（如果提供）
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return render_template('register.html', 
                             message='请输入有效的邮箱地址', 
                             username=username, email=email)
    
    # 连接数据库进行用户注册
    if not connect_database():
        return render_template('register.html', 
                             message='数据库连接失败，请稍后重试', 
                             username=username, email=email)
    
    try:
        # 确保用户表存在
        User.create_table_if_not_exists()
        
        # 创建新用户
        user = User.create_user(username, password, email)
        
        # 注册成功，重定向到登录页面
        return render_template('form.html', 
                             message='注册成功！请使用新账户登录', 
                             message_type='success')
    
    except ValueError as e:
        # 用户名已存在
        return render_template('register.html', 
                             message=str(e), 
                             username=username, email=email)
    
    except Exception as e:
        print(f"注册过程中出错: {e}")
        return render_template('register.html', 
                             message='注册失败，请稍后重试', 
                             username=username, email=email)
    finally:
        close_database()


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search_movie():
    """
    电影搜索
    ---
    tags:
      - 电影查询
    parameters:
      - name: year
        in: formData
        type: string
        required: true
        description: 年份，4位数字
    responses:
      200:
        description: 返回搜索页面或搜索结果
    """
    if request.method == 'GET':
        return render_template('search_movie.html')
    
    year = request.form.get('year', '').strip()
    
    # 年份格式验证
    if not re.fullmatch(r'^\d{4}$', year):
        return render_template('search_movie.html', 
                             error="请输入4位数字年份（如：2023）")
    
    # 年份范围验证
    year_int = int(year)
    if year_int < 1900 or year_int > 2030:
        return render_template('search_movie.html', 
                             error="请输入有效的年份范围（1900-2030）")
    
    # 查询数据库
    try:
        if not connect_database():
            return render_template('search_movie.html', 
                                 error="数据库连接失败，请稍后重试")
        
        movies = Movie.get_movies_by_year(year)
        movie_list = list(movies)
        
        return render_template('search_result.html', 
                             movies=movie_list, 
                             year=year,
                             count=len(movie_list))
        
    except Exception as e:
        print(f"数据库查询错误: {e}")
        return render_template('search_movie.html', 
                             error="查询失败，请稍后重试")
    finally:
        close_database()


@app.errorhandler(404)
def not_found_error(error):
    """404错误处理"""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="页面未找到"), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template('error.html', 
                         error_code=500, 
                         error_message="服务器内部错误"), 500


@app.before_request
def before_request():
    """请求前处理"""
    # 这里可以添加一些通用的请求前处理逻辑
    pass


@app.after_request
def after_request(response):
    """请求后处理"""
    # 添加一些安全头
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


def main():
    """主函数"""
    print("启动豆瓣电影Web应用...")
    print("=" * 40)
    print("访问地址: http://localhost:5000")
    print("API文档: http://localhost:5000/apidocs/")
    print("=" * 40)
    
    app.run(
        debug=FLASK_CONFIG['debug'],
        host='0.0.0.0',
        port=5000
    )


if __name__ == '__main__':
    main() 