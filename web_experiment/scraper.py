"""
豆瓣电影数据爬取模块
"""
import requests
import time
from pathlib import Path
from config import SCRAPER_CONFIG, FILE_PATHS


class DoubanScraper:
    """豆瓣电影数据爬取器"""
    
    def __init__(self):
        self.base_url = SCRAPER_CONFIG['url']
        self.headers = SCRAPER_CONFIG['headers']
        self.proxies = SCRAPER_CONFIG['proxies']
        self.output_file = FILE_PATHS['douban_html']
        self.total_pages = 10  # 豆瓣Top250共10页
        self.movies_per_page = 25  # 每页25部电影
    
    def fetch_data(self, retry_times=3, delay=1):
        """
        获取豆瓣电影Top250全部数据（10页）
        
        Args:
            retry_times (int): 重试次数
            delay (int): 重试间隔（秒）
            
        Returns:
            bool: 是否成功获取数据
        """
        print(f"开始获取豆瓣电影Top250数据（共{self.total_pages}页）...")
        all_pages_html = []
        
        for page in range(1, self.total_pages + 1):
            page_success = False
            start_index = (page - 1) * self.movies_per_page
            
            # 构建当前页面的URL
            if page == 1:
                url = self.base_url  # 第一页不需要start参数
            else:
                url = f"{self.base_url}?start={start_index}"
            
            # 尝试获取当前页面
            for attempt in range(retry_times):
                try:
                    print(f"正在获取第{page}页数据... (第{attempt + 1}次尝试)")
                    
                    response = requests.get(
                        url=url,
                        headers=self.headers,
                        proxies=self.proxies,
                        timeout=30
                    )
                    
                    response.raise_for_status()
                    all_pages_html.append(response.text)
                    print(f"✅ 第{page}页获取成功")
                    page_success = True
                    break
                    
                except requests.exceptions.RequestException as e:
                    print(f"❌ 第{page}页第{attempt + 1}次尝试失败: {e}")
                    if attempt < retry_times - 1:
                        print(f"等待{delay}秒后重试...")
                        time.sleep(delay)
            
            if not page_success:
                print(f"❌ 第{page}页获取失败，终止爬取")
                return False
            
            # 页面间隔，避免请求过快
            if page < self.total_pages:
                time.sleep(delay)
        
        # 合并所有页面数据并保存
        combined_html = self._combine_pages_html(all_pages_html)
        self._save_html(combined_html)
        
        print(f"✅ 成功获取全部{self.total_pages}页数据，已保存到 {self.output_file}")
        return True
    
    def _combine_pages_html(self, pages_html):
        """
        合并多个页面的HTML数据
        
        Args:
            pages_html (list): 多个页面的HTML内容列表
            
        Returns:
            str: 合并后的HTML内容
        """
        if not pages_html:
            return ""
        
        # 使用第一页作为基础模板
        base_html = pages_html[0]
        
        # 如果只有一页，直接返回
        if len(pages_html) == 1:
            return base_html
        
        try:
            from bs4 import BeautifulSoup
            
            # 解析第一页作为基础
            base_soup = BeautifulSoup(base_html, 'lxml')
            base_movie_list = base_soup.find('ol', class_='grid_view')
            
            if not base_movie_list:
                print("警告: 未找到电影列表容器，使用原始HTML")
                return '\n'.join(pages_html)
            
            # 从其他页面提取电影项并添加到基础列表中
            for page_html in pages_html[1:]:
                page_soup = BeautifulSoup(page_html, 'lxml')
                page_movie_list = page_soup.find('ol', class_='grid_view')
                
                if page_movie_list:
                    # 获取当前页面的所有电影项
                    movie_items = page_movie_list.find_all('li')
                    for item in movie_items:
                        base_movie_list.append(item)
            
            return str(base_soup)
            
        except ImportError:
            print("警告: BeautifulSoup不可用，直接连接HTML内容")
            return '\n'.join(pages_html)
        except Exception as e:
            print(f"警告: 合并HTML时出错 {e}，直接连接HTML内容")
            return '\n'.join(pages_html)
    
    def _save_html(self, html_content):
        """
        保存HTML内容到文件
        
        Args:
            html_content (str): HTML内容
        """
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except IOError as e:
            raise Exception(f"保存文件失败: {e}")
    
    def check_file_exists(self):
        """
        检查HTML文件是否存在
        
        Returns:
            bool: 文件是否存在
        """
        return Path(self.output_file).exists()
    
    def get_file_size(self):
        """
        获取HTML文件大小
        
        Returns:
            int: 文件大小（字节）
        """
        if self.check_file_exists():
            return Path(self.output_file).stat().st_size
        return 0


def main():
    """主函数"""
    scraper = DoubanScraper()
    
    # 检查是否已有数据文件
    if scraper.check_file_exists():
        file_size = scraper.get_file_size()
        print(f"检测到已有数据文件 {scraper.output_file} (大小: {file_size} 字节)")
        
        user_input = input("是否重新获取数据？(y/N): ").strip().lower()
        if user_input not in ['y', 'yes']:
            print("使用现有数据文件")
            return
    
    # 获取数据
    success = scraper.fetch_data()
    if not success:
        print("数据获取失败，请检查网络连接或稍后重试")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main()) 