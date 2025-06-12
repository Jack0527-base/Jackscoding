"""
项目配置文件
"""
import os

# 数据库配置
DATABASE_CONFIG = {
    'database': 'douban_top250',
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '06z05r27B',
    'charset': 'utf8mb4'
}

# Flask应用配置
FLASK_CONFIG = {
    'secret_key': 'your_secret_key_change_in_production',
    'debug': True
}

# 文件路径配置
FILE_PATHS = {
    'douban_html': 'douban.html',
    'csv_output': 'douban_top250.csv'
}

# 爬虫配置
SCRAPER_CONFIG = {
    'url': 'https://movie.douban.com/top250',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    },
    'proxies': {
        'http': None,
        'https': None
    }
}

# 默认用户配置（仅用于演示，生产环境应使用数据库）
DEFAULT_USER = {
    'username': 'Jack',
    'password': 'password'
} 