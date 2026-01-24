import requests
from bs4 import BeautifulSoup
import re
import time
import os
from datetime import datetime
from collections import OrderedDict

class LotteryCrawler:
    def __init__(self):
        self.base_urls = {
            'ssq': 'https://m.ssqzj.com/kaijiang/ssq/',
            '3d': 'https://m.ssqzj.com/kaijiang/3d/',
            'kl8': 'https://m.ssqzj.com/kaijiang/fckl8/'
        }
        self.output_dir = 'fc'
        self.output_files = {
            'ssq': 'ssq.txt',
            '3d': 'sd.txt',
            'kl8': 'kl8.txt'
        }
        
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def fetch_page(self, url, max_retries=3):
        """获取网页内容"""
        for i in range(max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                return response.text
            except Exception as e:
                print(f"请求失败 {url}: {e}, 重试 {i+1}/{max_retries}")
                if i < max_retries - 1:
                    time.sleep(2)
                else:
                    return None
    
    def parse_ssq(self, html):
        """解析双色球数据"""
        soup = BeautifulSoup(html, 'html.parser')
        data = []
        
        # 查找最新开奖结果
        results = soup.find_all("div", class_="kb_num kj_num public_num")
        for result in results:
            period_text = result.get_text(strip=True)
            period_match = re.search(r"第(\d+)期", period_text)
            if not period_match:
                continue
            
            period_num = period_match.group(1)
            
            # 提取红球和蓝球
            red_balls = [num.get_text(strip=True).zfill(2) for num in result.find_all("span", class_="qiu_red")]
            blue_ball = None
            blue_elem = result.find("span", class_="qiu_blue")
            if blue_elem:
                blue_ball = blue_elem.get_text(strip=True).zfill(2)
            
            if red_balls and blue_ball and len(red_balls) == 6:
                data.append({
                    'period': period_num,
                    'red': red_balls,
                    'blue': blue_ball
                })
        
        # 查找历史开奖结果
        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
        for index, result in enumerate(results):
            period_text = result.get_text(strip=True)
            period_match = re.search(r"第(\d+)期", period_text)
            if not period_match:
                continue
            
            period_num = period_match.group(1)
            
            # 提取号码
            if index == 0:
                red_balls = [num.get_text(strip=True).zfill(2) for num in result.find_all("span", class_="qiu_red")]
                blue_elem = result.find("span", class_="qiu_blue")
            else:
                red_balls = [num.get_text(strip=True).zfill(2) for num in result.find_all("span", class_="red_white")]
                blue_elem = result.find("span", class_="blue_white")
            
            blue_ball = None
            if blue_elem:
                blue_ball = blue_elem.get_text(strip=True).zfill(2)
            
            if red_balls and blue_ball and len(red_balls) == 6:
                data.append({
                    'period': period_num,
                    'red': red_balls,
                    'blue': blue_ball
                })
        
        return data
    
    def parse_3d(self, html):
        """解析3D数据"""
        soup = BeautifulSoup(html, 'html.parser')
        data = []
        
        # 查找最新开奖结果
        results = soup.find_all("div", class_="kb_num kj_num public_num")
        for result in results:
            period_text = result.get_text(strip=True)
            period_match = re.search(r"第(\d+)期", period_text)
            if not period_match:
                continue
            
            period_num = period_match.group(1)
            
            # 提取号码
            numbers = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
            if len(numbers) == 3:
                data.append({
                    'period': period_num,
                    'numbers': numbers
                })
        
        # 查找历史开奖结果
        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
        for index, result in enumerate(results):
            period_text = result.get_text(strip=True)
            period_match = re.search(r"第(\d+)期", period_text)
            if not period_match:
                continue
            
            period_num = period_match.group(1)
            
            # 提取号码
            if index == 0:
                numbers = [num.get_text(strip=True) for num in result.find_all("span", class_="qiu_red")]
            else:
                numbers = [num.get_text(strip=True) for num in result.find_all("span", class_="red_white")]
            
            if len(numbers) == 3:
                data.append({
                    'period': period_num,
                    'numbers': numbers
                })
        
        return data
    
    def parse_kl8(self, html):
        """解析快乐8数据"""
        soup = BeautifulSoup(html, 'html.parser')
        data = []
        
        # 查找最新开奖结果
        results = soup.find_all("div", class_="kb_num kj_num public_num")
        for result in results:
            period_text = result.get_text(strip=True)
            period_match = re.search(r"第(\d+)期", period_text)
            if not period_match:
                continue
            
            period_num = period_match.group(1)
            
            # 提取号码
            numbers = [num.get_text(strip=True).zfill(2) for num in result.find_all("span", class_="qiu_red")]
            if len(numbers) == 20:
                data.append({
                    'period': period_num,
                    'numbers': numbers
                })
        
        # 查找历史开奖结果
        results = soup.find_all("div", class_="kb_num kj_num kj_erj")
        for index, result in enumerate(results):
            period_text = result.get_text(strip=True)
            period_match = re.search(r"第(\d+)期", period_text)
            if not period_match:
                continue
            
            period_num = period_match.group(1)
            
            # 提取号码
            if index == 0:
                numbers = [num.get_text(strip=True).zfill(2) for num in result.find_all("span", class_="qiu_red")]
            else:
                numbers = [num.get_text(strip=True).zfill(2) for num in result.find_all("span", class_="red_white")]
            
            if len(numbers) == 20:
                data.append({
                    'period': period_num,
                    'numbers': numbers
                })
        
        return data
    
    def crawl_all_pages(self, lottery_type):
        """爬取所有页面的数据"""
        base_url = self.base_urls[lottery_type]
        all_data = []
        page = 1
        max_pages = 50  # 设置最大页数，防止无限循环
        seen_periods = set()  # 用于去重
        
        print(f"开始爬取 {lottery_type} 数据...")
        
        while page <= max_pages:
            try:
                if page == 1:
                    url = base_url
                else:
                    url = f"{base_url}p{page}/"
                
                print(f"正在爬取第 {page} 页: {url}")
                html = self.fetch_page(url)
                
                if not html:
                    print(f"第 {page} 页获取失败，停止爬取")
                    break
                
                # 根据彩种类型解析数据
                if lottery_type == 'ssq':
                    page_data = self.parse_ssq(html)
                elif lottery_type == '3d':
                    page_data = self.parse_3d(html)
                elif lottery_type == 'kl8':
                    page_data = self.parse_kl8(html)
                else:
                    break
                
                # 去重并添加到总数据
                for item in page_data:
                    period = item['period']
                    if period not in seen_periods:
                        seen_periods.add(period)
                        all_data.append(item)
                
                if not page_data:
                    print(f"第 {page} 页没有数据，停止爬取")
                    break
                
                print(f"第 {page} 页获取到 {len(page_data)} 条数据，累计 {len(all_data)} 条")
                
                page += 1
                time.sleep(1)  # 防止请求过快
                
            except Exception as e:
                print(f"爬取第 {page} 页时出错: {e}")
                break
        
        print(f"{lottery_type} 爬取完成，共获取 {len(all_data)} 条数据")
        return all_data
    
    def extract_year_from_period(self, period):
        """从期号中提取年份"""
        # 期号格式可能是：2024001 或 001
        # 如果是6位或7位数字，前4位是年份
        if len(period) >= 6:
            year_str = period[:4]
            if year_str.isdigit():
                return int(year_str)
        # 如果期号较短，尝试从当前日期推断
        current_year = datetime.now().year
        return current_year
    
    def format_ssq_data(self, data):
        """格式化双色球数据"""
        red_str = ' '.join(data['red'])
        return f"第{data['period']}期: {red_str} + {data['blue']}"
    
    def format_3d_data(self, data):
        """格式化3D数据"""
        numbers_str = ' '.join(data['numbers'])
        return f"第{data['period']}期: {numbers_str}"
    
    def format_kl8_data(self, data):
        """格式化快乐8数据"""
        numbers = data['numbers']
        line1 = ' '.join(numbers[:10])
        line2 = ' '.join(numbers[10:])
        return f"第{data['period']}期: {line1}\n        {line2}"
    
    def save_to_file(self, lottery_type, all_data):
        """保存数据到文件，按年份倒序排列，年份之间空2行"""
        if not all_data:
            print(f"{lottery_type} 没有数据需要保存")
            return
        
        # 按年份分组
        year_data = {}
        for item in all_data:
            year = self.extract_year_from_period(item['period'])
            if year not in year_data:
                year_data[year] = []
            year_data[year].append(item)
        
        # 按年份倒序排列
        sorted_years = sorted(year_data.keys(), reverse=True)
        
        # 格式化数据
        output_lines = []
        for year in sorted_years:
            # 按期号排序（倒序，最新的在前）
            year_items = sorted(year_data[year], key=lambda x: int(x['period']), reverse=True)
            
            for item in year_items:
                if lottery_type == 'ssq':
                    output_lines.append(self.format_ssq_data(item))
                elif lottery_type == '3d':
                    output_lines.append(self.format_3d_data(item))
                elif lottery_type == 'kl8':
                    output_lines.append(self.format_kl8_data(item))
            
            # 年份之间空2行（最后一个年份后不添加空行）
            if year != sorted_years[-1]:
                output_lines.append('')
                output_lines.append('')
        
        # 写入文件
        output_file = os.path.join(self.output_dir, self.output_files[lottery_type])
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        print(f"{lottery_type} 数据已保存到 {output_file}，共 {len(all_data)} 条记录")
    
    def run(self):
        """运行爬虫"""
        self.ensure_output_dir()
        
        # 爬取三个彩种
        for lottery_type in ['ssq', '3d', 'kl8']:
            try:
                all_data = self.crawl_all_pages(lottery_type)
                self.save_to_file(lottery_type, all_data)
            except Exception as e:
                print(f"处理 {lottery_type} 时出错: {e}")
                continue
        
        print("所有彩种数据爬取完成！")


if __name__ == '__main__':
    crawler = LotteryCrawler()
    crawler.run()
