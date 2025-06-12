# 豆瓣电影数据采集与查询系统

一个基于Flask的豆瓣电影数据采集、处理和查询系统，支持Web界面和API接口。

## 🎬 项目简介

本项目是一个完整的电影数据管理系统，主要功能包括：

- **数据采集**: 从豆瓣电影Top250获取完整的250部电影信息（遍历全部10页）
- **数据处理**: 解析HTML并存储到MySQL数据库和CSV文件
- **用户系统**: 基于MySQL的用户注册、登录认证系统（密码加密存储）
- **Web界面**: 提供用户友好的电影搜索和浏览界面
- **API接口**: 支持RESTful API，并提供Swagger文档

## 🏗️ 项目结构

```
web_experiment/
├── config.py              # 配置文件
├── models.py               # 数据库模型
├── scraper.py              # 数据爬取模块
├── data_processor.py       # 数据处理模块
├── app.py                  # Flask Web应用
├── main.py                 # 主运行脚本
├── requirements.txt        # 项目依赖
├── README.md              # 项目文档
├── templates/             # HTML模板文件
│   ├── home.html          # 首页
│   ├── form.html          # 登录页面
│   ├── register.html      # 注册页面
│   ├── search_movie.html  # 电影搜索页面
│   ├── search_result.html # 搜索结果页面
│   ├── signin-ok.html     # 登录成功页面
│   └── error.html         # 错误页面
├── douban.html            # 爬取的HTML数据（自动生成）
├── douban_top250.csv      # 导出的CSV数据（自动生成）
└── UML/                   # 项目设计文档
    ├── 网上购物系统.png
    └── shoppingSystemUML.promt
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 8.0+
- 推荐使用虚拟环境

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd web_experiment
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置数据库**
   
   创建MySQL数据库：
   ```sql
   CREATE DATABASE douban_top250 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   
   修改 `config.py` 中的数据库配置：
   ```python
   DATABASE_CONFIG = {
       'database': 'douban_top250',
       'host': 'localhost',
       'port': 3306,
       'user': 'your_username',
       'password': 'your_password',
       'charset': 'utf8mb4'
   }
   ```

5. **初始化数据库**
   ```bash
   # 初始化数据库（创建表和默认用户）
   python main.py init
   ```

6. **运行项目**
   ```bash
   # 运行完整工作流程（推荐）
   python main.py all
   
   # 或分步执行
   python main.py fetch    # 获取豆瓣Top250完整数据（250部电影）
   python main.py process  # 处理电影数据（250部电影）
   python main.py web      # 启动Web应用
   ```

## 📖 使用说明

### 命令行工具

项目提供了统一的命令行管理工具 `main.py`：

```bash
# 获取豆瓣Top250完整数据（全部10页，250部电影）
python main.py fetch

# 处理电影数据（解析并存储250部电影）
python main.py process

# 启动Web应用
python main.py web

# 检查数据库状态
python main.py check

# 显示项目状态
python main.py status

# 运行完整工作流程
python main.py all
```

### Web界面使用

1. **访问首页**: http://localhost:5000
2. **用户注册**: 新用户可以注册账户（支持邮箱字段）
3. **用户登录**: 
   - **默认管理员**: 用户名 `admin`，密码 `admin123`
   - **测试用户**: 用户名 `Jack`，密码 `password`
   - **自定义用户**: 使用注册功能创建的用户
4. **电影搜索**: 登录后可按年份搜索电影
5. **API文档**: http://localhost:5000/apidocs/

### API接口

项目提供RESTful API接口，支持Swagger文档：

- **API文档地址**: http://localhost:5000/apidocs/
- **接口格式**: JSON
- **主要端点**:
  - `GET /`: 首页
  - `POST /signin`: 用户登录
  - `POST /search`: 电影搜索

## 🛠️ 技术栈

### 后端技术
- **Web框架**: Flask 2.3.3
- **数据库ORM**: Peewee 3.16.3
- **数据库**: MySQL 8.0
- **HTML解析**: BeautifulSoup4 + lxml
- **HTTP请求**: Requests
- **API文档**: Flasgger (Swagger)

### 前端技术
- **模板引擎**: Jinja2
- **样式**: 原生CSS (响应式设计)
- **JavaScript**: 原生JS (最小化使用)

## 📊 数据说明

### 数据来源
- **来源**: 豆瓣电影Top250（完整10页数据）
- **数据量**: 精确250部电影
- **获取方式**: 自动遍历全部10个页面
- **更新频率**: 手动更新

### 数据字段

#### 电影表 (douban_movie)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT(AutoField) | 电影ID |
| title | VARCHAR(200) | 电影名称 |
| rating_num | FLOAT | 评价分数 |
| comment_num | INT | 评论人数 |
| directors | VARCHAR(200) | 导演 |
| actors | VARCHAR(200) | 主演 |
| year | VARCHAR(10) | 上映年份 |
| country | VARCHAR(100) | 出品地 |
| category | VARCHAR(100) | 剧情类别 |
| pic | VARCHAR(500) | 电影海报链接 |

#### 用户表 (users)
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT(AutoField) | 用户ID |
| username | VARCHAR(50) | 用户名（唯一） |
| password_hash | VARCHAR(128) | 密码哈希值 |
| email | VARCHAR(100) | 邮箱地址（可选） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| is_active | INT | 是否激活（1=激活，0=禁用） |

## 🔧 配置说明

### 主要配置文件：`config.py`

```python
# 数据库配置
DATABASE_CONFIG = {
    'database': 'douban_top250',    # 数据库名
    'host': 'localhost',            # 数据库主机
    'port': 3306,                   # 数据库端口
    'user': 'root',                 # 数据库用户名
    'password': 'your_password',    # 数据库密码
    'charset': 'utf8mb4'            # 字符集
}

# Flask应用配置
FLASK_CONFIG = {
    'secret_key': 'your_secret_key',  # Session密钥
    'debug': True                     # 调试模式
}

# 文件路径配置
FILE_PATHS = {
    'douban_html': 'douban.html',         # HTML数据文件
    'csv_output': 'douban_top250.csv'     # CSV输出文件
}
```

## 🚨 注意事项

1. **数据库连接**: 确保MySQL服务正在运行，并且配置正确
2. **网络访问**: 数据爬取需要稳定的网络连接
3. **字符编码**: 数据库和文件均使用UTF-8编码
4. **安全考虑**: 
   - 生产环境请更改默认密码和密钥
   - 考虑添加用户管理和权限控制
5. **合规使用**: 请遵守豆瓣网站的robots.txt和使用协议

## 🐛 常见问题

### 1. 数据库连接失败
```bash
# 检查MySQL服务状态
systemctl status mysql  # Linux
brew services list | grep mysql  # Mac

# 检查数据库配置
python main.py check
```

### 2. 爬取数据失败
- 检查网络连接
- 确认豆瓣网站可访问
- 检查User-Agent是否被封禁

### 3. 模块导入错误
```bash
# 重新安装依赖
pip install -r requirements.txt

# 检查Python环境
python --version
pip list
```

## 📈 功能特性

### ✅ 已实现功能
- [x] 豆瓣电影数据爬取（完整250部电影）
- [x] HTML数据解析和数据验证
- [x] 数据库存储（MySQL）
- [x] CSV数据导出
- [x] Web用户界面（响应式设计）
- [x] **用户注册功能**（支持邮箱验证）
- [x] **用户登录认证**（基于数据库）
- [x] **密码加密存储**（SHA256+盐值）
- [x] **用户会话管理**
- [x] 电影搜索功能（按年份）
- [x] API接口（Swagger文档）
- [x] 错误处理和日志
- [x] 数据库初始化和管理

### 🔮 未来计划
- [ ] 用户权限管理和角色系统
- [ ] 电影收藏和评论功能
- [ ] 高级搜索（多条件筛选：导演、类型、评分等）
- [ ] 用户个人中心（密码修改、个人信息）
- [ ] 数据可视化图表（评分分布、年份统计等）
- [ ] 定时数据更新和增量爬取
- [ ] Redis缓存机制优化
- [ ] 单元测试覆盖
- [ ] Docker容器化部署

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目仅供学习和研究使用。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues](项目地址/issues)
- 邮箱: your-email@example.com

---

**⭐ 如果这个项目对您有帮助，请给个星标支持！** 