#!/usr/bin/env python3
"""
豆瓣电影项目主运行脚本
"""
import argparse
import sys
from pathlib import Path

# 导入项目模块
from scraper import DoubanScraper
from data_processor import MovieDataProcessor
from models import connect_database, close_database, Movie, User


def fetch_data():
    """获取豆瓣电影Top250完整数据（10页，250部电影）"""
    print("🎬 开始获取豆瓣电影Top250完整数据...")
    scraper = DoubanScraper()
    
    if scraper.fetch_data():
        print("✅ 数据获取成功！已获取全部250部电影信息")
        return True
    else:
        print("❌ 数据获取失败！")
        return False


def process_data():
    """处理豆瓣Top250电影数据（250部电影）"""
    print("📊 开始处理豆瓣Top250电影数据...")
    processor = MovieDataProcessor()
    
    if processor.process_and_save():
        print("✅ 数据处理成功！已处理全部250部电影")
        return True
    else:
        print("❌ 数据处理失败！")
        return False


def run_web_app():
    """运行Web应用"""
    print("🌐 启动Web应用...")
    try:
        from app import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Web应用已停止")
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保安装了所有依赖: pip install -r requirements.txt")


def init_database():
    """初始化数据库（创建表和默认用户）"""
    print("🔧 正在初始化数据库...")
    
    if not connect_database():
        print("❌ 数据库连接失败！")
        return False
    
    try:
        # 创建所有表
        from models import db
        db.create_tables([User, Movie], safe=True)
        print("✅ 数据库表创建成功")
        
        # 检查是否存在默认管理员用户
        if not User.select().where(User.username == 'admin').exists():
            # 创建默认管理员用户
            admin_user = User.create_user('admin', 'admin123', 'admin@example.com')
            print("✅ 默认管理员用户创建成功 (用户名: admin, 密码: admin123)")
        else:
            print("ℹ️  默认管理员用户已存在")
        
        # 检查是否存在测试用户Jack
        if not User.select().where(User.username == 'Jack').exists():
            # 创建测试用户
            jack_user = User.create_user('Jack', 'password', 'jack@example.com')
            print("✅ 测试用户Jack创建成功 (用户名: Jack, 密码: password)")
        else:
            print("ℹ️  测试用户Jack已存在")
        
        return True
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False
    finally:
        close_database()


def check_database():
    """检查数据库连接和数据"""
    print("🔍 检查数据库连接...")
    
    if not connect_database():
        print("❌ 数据库连接失败！")
        return False
    
    try:
        # 检查表是否存在
        Movie.create_table_if_not_exists()
        User.create_table_if_not_exists()
        
        # 统计电影数量
        movie_count = Movie.select().count()
        print(f"✅ 数据库连接成功！当前有 {movie_count} 部电影")
        
        # 统计用户数量
        user_count = User.select().count()
        print(f"👥 当前有 {user_count} 个用户")
        
        if movie_count > 0:
            # 显示一些示例数据
            sample_movies = Movie.select().limit(3)
            print("\n📽️  示例电影数据:")
            for movie in sample_movies:
                print(f"  - {movie.title} ({movie.year}) - 评分: {movie.rating_num}")
        
        if user_count > 0:
            # 显示用户信息
            sample_users = User.select().limit(3)
            print("\n👤 示例用户数据:")
            for user in sample_users:
                print(f"  - {user.username} (邮箱: {user.email or '未设置'})")
        
        return True
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    finally:
        close_database()


def show_status():
    """显示项目状态"""
    print("📋 项目状态检查")
    print("=" * 50)
    
    # 检查文件
    scraper = DoubanScraper()
    processor = MovieDataProcessor()
    
    print("📁 文件状态:")
    if scraper.check_file_exists():
        size = scraper.get_file_size()
        print(f"  ✅ HTML数据文件: {scraper.output_file} ({size} 字节)")
    else:
        print(f"  ❌ HTML数据文件: {scraper.output_file} (不存在)")
    
    if Path(processor.csv_file).exists():
        print(f"  ✅ CSV文件: {processor.csv_file}")
    else:
        print(f"  ❌ CSV文件: {processor.csv_file} (不存在)")
    
    # 检查数据库
    print("\n💾 数据库状态:")
    check_database()


def full_workflow():
    """完整的工作流程：初始化数据库 -> 获取豆瓣Top250全部数据 -> 处理数据 -> 启动Web应用"""
    print("🚀 开始豆瓣Top250完整工作流程...")
    print("=" * 50)
    
    # 步骤0: 初始化数据库
    if not init_database():
        print("❌ 工作流程中断：数据库初始化失败")
        return False
    
    # 步骤1: 获取数据
    if not fetch_data():
        print("❌ 工作流程中断：数据获取失败")
        return False
    
    # 步骤2: 处理数据
    if not process_data():
        print("❌ 工作流程中断：数据处理失败")
        return False
    
    # 步骤3: 检查数据库
    if not check_database():
        print("❌ 工作流程中断：数据库检查失败")
        return False
    
    print("\n✅ 数据准备完成！")
    print("🌐 是否启动Web应用？(y/N): ", end="")
    
    user_input = input().strip().lower()
    if user_input in ['y', 'yes']:
        run_web_app()
    else:
        print("👋 您可以稍后运行 'python main.py web' 来启动Web应用")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="豆瓣电影项目管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py init       # 初始化数据库（创建表和默认用户）
  python main.py fetch      # 获取豆瓣Top250完整数据（250部电影）
  python main.py process    # 处理电影数据（250部电影）
  python main.py web        # 启动Web应用
  python main.py check      # 检查数据库状态
  python main.py status     # 显示项目状态
  python main.py all        # 运行完整工作流程
        """
    )
    
    parser.add_argument(
        'command',
        choices=['fetch', 'process', 'web', 'check', 'status', 'init', 'all'],
        help='要执行的命令'
    )
    
    args = parser.parse_args()
    
    print("🎬 豆瓣电影项目管理工具")
    print("=" * 50)
    
    if args.command == 'fetch':
        success = fetch_data()
    elif args.command == 'process':
        success = process_data()
    elif args.command == 'web':
        run_web_app()
        success = True
    elif args.command == 'check':
        success = check_database()
    elif args.command == 'status':
        show_status()
        success = True
    elif args.command == 'init':
        success = init_database()
    elif args.command == 'all':
        success = full_workflow()
    else:
        parser.print_help()
        success = False
    
    if not success and args.command != 'web':
        sys.exit(1)


if __name__ == '__main__':
    main() 