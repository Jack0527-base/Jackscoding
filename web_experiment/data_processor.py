"""
豆瓣电影数据处理模块
"""
import csv
import re
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from config import FILE_PATHS
from models import Movie, User, connect_database, close_database


class MovieDataProcessor:
    """电影数据处理器"""
    
    def __init__(self):
        self.html_file = FILE_PATHS['douban_html']
        self.csv_file = FILE_PATHS['csv_output']
        self.headers = [
            '电影名称', '评价分数', '评论人数',
            '导演', '主演', '上映时间',
            '出品地', '剧情类别', '电影标题图链接'
        ]
    
    def parse_html_file(self) -> List[Dict]:
        """
        解析HTML文件，提取电影信息
        
        Returns:
            List[Dict]: 电影信息列表
        """
        if not Path(self.html_file).exists():
            raise FileNotFoundError(f"HTML文件不存在: {self.html_file}")
        
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
        except IOError as e:
            raise Exception(f"读取HTML文件失败: {e}")
        
        return self._extract_movies_from_html(html_content)
    
    def _extract_movies_from_html(self, html_content: str) -> List[Dict]:
        """
        从HTML内容中提取电影信息
        
        Args:
            html_content (str): HTML内容
            
        Returns:
            List[Dict]: 电影信息列表
        """
        soup = BeautifulSoup(html_content, 'lxml')
        movies = []
        
        # 查找电影列表容器
        movie_container = soup.find('ol', class_='grid_view')
        if not movie_container:
            print("警告: 未找到电影列表容器")
            return movies
        
        movie_items = movie_container.find_all('li')
        print(f"找到 {len(movie_items)} 部电影")
        
        for i, movie_item in enumerate(movie_items[:250], 1):  # 限制最多250部
            try:
                movie_info = self._parse_single_movie(movie_item)
                if movie_info:
                    movies.append(movie_info)
                    if i % 50 == 0:
                        print(f"已处理 {i} 部电影...")
            except Exception as e:
                print(f"解析第 {i} 部电影时出错: {e}")
                continue
        
        print(f"成功解析 {len(movies)} 部电影")
        return movies
    
    def _parse_single_movie(self, movie_item) -> Optional[Dict]:
        """
        解析单个电影信息
        
        Args:
            movie_item: BeautifulSoup电影元素
            
        Returns:
            Optional[Dict]: 电影信息字典
        """
        try:
            # 电影名称
            title_elem = movie_item.find('div', class_='hd').find('span', class_='title')
            title = title_elem.get_text(strip=True) if title_elem else "未知"
            
            # 评分
            rating_elem = movie_item.find('span', class_='rating_num')
            rating_num = float(rating_elem.get_text(strip=True)) if rating_elem else 0.0
            
            # 评论人数
            comment_elem = movie_item.find('div', class_='bd').find('div').find_all('span')[-1]
            comment_text = comment_elem.get_text(strip=True)
            comment_num = int(re.sub(r'[^\d]', '', comment_text)) if comment_text else 0
            
            # 导演和主演信息
            info_p = movie_item.find('div', class_='bd').find('p')
            info_lines = info_p.get_text(strip=True, separator='\n').split('\n')
            
            directors, actors = self._parse_director_actor_info(info_lines[0] if info_lines else "")
            
            # 年份、国家、类型
            year, country, category = self._parse_movie_details(info_lines[1] if len(info_lines) > 1 else "")
            
            # 电影海报
            pic_elem = movie_item.find('img')
            pic = pic_elem.get('src') if pic_elem else ""
            
            return {
                'title': title,
                'rating_num': rating_num,
                'comment_num': comment_num,
                'directors': directors,
                'actors': actors,
                'year': year,
                'country': country,
                'category': category,
                'pic': pic
            }
            
        except Exception as e:
            print(f"解析电影信息时出错: {e}")
            return None
    
    def _parse_director_actor_info(self, info_line: str) -> tuple:
        """
        解析导演和主演信息
        
        Args:
            info_line (str): 信息行
            
        Returns:
            tuple: (导演, 主演)
        """
        directors, actors = "", ""
        
        if '导演:' in info_line:
            parts = info_line.split('导演:')[1].strip()
            if '主演:' in parts:
                directors, actors = parts.split('主演:', 1)
                directors = directors.strip()
                actors = actors.strip()
            else:
                directors = parts.strip()
        
        return directors, actors
    
    def _parse_movie_details(self, detail_line: str) -> tuple:
        """
        解析电影详细信息（年份、国家、类型）
        
        Args:
            detail_line (str): 详细信息行
            
        Returns:
            tuple: (年份, 国家, 类型)
        """
        parts = detail_line.split('/')
        year = parts[0].strip() if len(parts) > 0 else ""
        country = parts[1].strip() if len(parts) > 1 else ""
        category = parts[2].strip() if len(parts) > 2 else ""
        
        return year, country, category
    
    def save_to_csv(self, movies: List[Dict]) -> bool:
        """
        保存电影信息到CSV文件
        
        Args:
            movies (List[Dict]): 电影信息列表
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.headers)
                
                for movie in movies:
                    row = [
                        movie['title'], movie['rating_num'], movie['comment_num'],
                        movie['directors'], movie['actors'], movie['year'],
                        movie['country'], movie['category'], movie['pic']
                    ]
                    writer.writerow(row)
            
            print(f"数据已保存到CSV文件: {self.csv_file}")
            return True
            
        except Exception as e:
            print(f"保存CSV文件失败: {e}")
            return False
    
    def save_to_database(self, movies: List[Dict]) -> bool:
        """
        保存电影信息到数据库
        
        Args:
            movies (List[Dict]): 电影信息列表
            
        Returns:
            bool: 是否保存成功
        """
        if not connect_database():
            return False
        
        try:
            # 创建表
            Movie.create_table_if_not_exists()
            
            # 清理旧数据
            old_count = Movie.select().count()
            if old_count > 0:
                Movie.delete().execute()
                print(f"已清理 {old_count} 条旧记录")
            
            # 批量插入新数据
            Movie.bulk_insert(movies)
            
            print(f"数据已保存到数据库，共 {len(movies)} 条记录")
            return True
            
        except Exception as e:
            print(f"保存到数据库失败: {e}")
            return False
        finally:
            close_database()
    
    def process_and_save(self, save_csv=True, save_db=True) -> bool:
        """
        处理并保存数据
        
        Args:
            save_csv (bool): 是否保存到CSV
            save_db (bool): 是否保存到数据库
            
        Returns:
            bool: 是否处理成功
        """
        try:
            print("开始解析电影数据...")
            movies = self.parse_html_file()
            
            if not movies:
                print("未找到有效的电影数据")
                return False
            
            success = True
            
            if save_csv:
                success &= self.save_to_csv(movies)
            
            if save_db:
                success &= self.save_to_database(movies)
            
            return success
            
        except Exception as e:
            print(f"数据处理失败: {e}")
            return False


def main():
    """主函数"""
    processor = MovieDataProcessor()
    
    print("豆瓣电影数据处理器")
    print("=" * 40)
    
    success = processor.process_and_save()
    
    if success:
        print("数据处理完成！")
        return 0
    else:
        print("数据处理失败！")
        return 1


if __name__ == '__main__':
    exit(main()) 