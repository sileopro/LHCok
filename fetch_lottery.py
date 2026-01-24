#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票数据抓取脚本
从网站抓取双色球、3D、快乐8的历史记录
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import time
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 网站URL模板（主数据源）
URLS = {
    'ssq': 'https://www.55128.cn/kjh/history_fcssq.aspx?year={year}',
    'sd': 'https://www.55128.cn/kjh/history_fcsd.aspx?year={year}',
    'kl8': 'https://www.55128.cn/kjh/history_fckl8.aspx?year={year}'
}


# 输出文件路径
OUTPUT_DIR = 'fc'
OUTPUT_FILES = {
    'ssq': os.path.join(OUTPUT_DIR, 'ssq.txt'),
    'sd': os.path.join(OUTPUT_DIR, 'sd.txt'),
    'kl8': os.path.join(OUTPUT_DIR, 'kl8.txt')
}

# 请求头（完整版，模拟真实浏览器）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://www.55128.cn/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Cache-Control': 'max-age=0'
}


def get_current_year():
    """获取当前年份"""
    return datetime.now().year

def test_connection():
    """测试网络连接"""
    print("测试网络连接...")
    test_urls = [
        'https://www.55128.cn/',
        'https://www.baidu.com/',  # 测试基本网络连接
    ]
    
    for test_url in test_urls:
        try:
            response = requests.get(test_url, timeout=5, verify=False)
            if response.status_code == 200:
                print(f"✓ 可以访问: {test_url}")
                return True
        except:
            pass
    
    print("✗ 网络连接测试失败")
    return False

def fetch_page(url, retry=3):
    """抓取网页内容，支持重试（参考 happy8_crawler.py 的简单方式）"""
    sess = requests.Session()
    sess.headers.update(HEADERS)
    
    # 先访问主页获取 cookies（可能有助于连接）
    try:
        base_url = '/'.join(url.split('/')[:3])
        sess.get(base_url, timeout=10, verify=False)
        time.sleep(1)
    except:
        pass
    
    for attempt in range(retry):
        try:
            # 使用简单的方式获取（参考 happy8_crawler.py）
            response = sess.get(url, timeout=30, verify=False, allow_redirects=True)
            
            # 自动检测编码
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding or 'utf-8'
            else:
                response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return response.text
            elif response.status_code == 403:
                print(f"403 禁止访问 (尝试 {attempt + 1}/{retry}) {url}")
                if attempt < retry - 1:
                    time.sleep(3)
            else:
                print(f"HTTP错误 {response.status_code}: {url}")
        except requests.exceptions.SSLError as e:
            print(f"SSL错误 (尝试 {attempt + 1}/{retry}) {url}: {e}")
            if attempt < retry - 1:
                time.sleep(2)
        except requests.exceptions.ConnectionError as e:
            print(f"连接错误 (尝试 {attempt + 1}/{retry}) {url}: {e}")
            if attempt < retry - 1:
                time.sleep(3)  # 连接错误时等待
        except Exception as e:
            print(f"抓取失败 (尝试 {attempt + 1}/{retry}) {url}: {e}")
            if attempt < retry - 1:
                time.sleep(2)
    return None

def parse_ssq(html, year):
    """解析双色球数据"""
    records = []
    # 优先使用 lxml，如果失败则使用 html.parser（参考 happy8_crawler.py）
    try:
        soup = BeautifulSoup(html, 'lxml')
    except:
        soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有表格
    tables = soup.find_all('table')
    seen_periods = set()  # 用于去重
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:  # 至少需要3列：开奖时间、期数、号码
                continue
            
            # 跳过表头
            first_cell_text = cells[0].get_text(strip=True).upper()
            if first_cell_text in ['开奖时间', '期号', '期数', 'PERIOD', '期', '开奖日期']:
                continue
            
            # 提取期号（从第2列，索引1）
            period_text = cells[1].get_text(strip=True)
            # 匹配7位期号（如2026010）或3位期号（如010）
            period_match = re.search(r'(\d{7}|\d{3})', period_text)
            if not period_match:
                continue
            
            period = period_match.group(1)
            if len(period) == 7:
                period = period[-3:]  # 取后3位
            period = period.zfill(3)
            
            # 去重
            if period in seen_periods:
                continue
            seen_periods.add(period)
            
            # 提取号码（从第3列，索引2，即"号码"列）
            numbers_cell = cells[2]
            numbers_text = numbers_cell.get_text(strip=True)
            
            # 提取所有数字
            all_nums = re.findall(r'\d+', numbers_text)
            red_balls = []
            blue_balls = []
            
            for n in all_nums:
                num = int(n)
                if 1 <= num <= 33:  # 红球范围
                    red_balls.append(num)
                elif 1 <= num <= 16:  # 蓝球范围
                    blue_balls.append(num)
            
            # 去重并排序
            red_balls = sorted(list(set(red_balls)))
            blue_balls = sorted(list(set(blue_balls)))
            
            # 双色球：6个红球 + 1个蓝球
            if len(red_balls) >= 6 and len(blue_balls) >= 1:
                records.append({
                    'period': period,
                    'red': red_balls[:6],
                    'blue': blue_balls[0]
                })
    
    return records

def parse_sd(html, year):
    """解析3D数据"""
    records = []
    # 优先使用 lxml，如果失败则使用 html.parser
    try:
        soup = BeautifulSoup(html, 'lxml')
    except:
        soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有表格
    tables = soup.find_all('table')
    seen_periods = set()  # 用于去重
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:  # 至少需要3列：开奖时间、期数、号码
                continue
            
            # 跳过表头
            first_cell_text = cells[0].get_text(strip=True).upper()
            if first_cell_text in ['开奖时间', '期号', '期数', 'PERIOD', '期', '开奖日期']:
                continue
            
            # 提取期号（从第2列，索引1）
            period_text = cells[1].get_text(strip=True)
            # 匹配7位期号（如2026023）或3位期号（如023）
            period_match = re.search(r'(\d{7}|\d{3})', period_text)
            if not period_match:
                continue
            
            period = period_match.group(1)
            if len(period) == 7:
                period = period[-3:]  # 取后3位
            period = period.zfill(3)
            
            # 去重
            if period in seen_periods:
                continue
            seen_periods.add(period)
            
            # 提取号码（从第3列，索引2，即"号码"列）
            numbers_cell = cells[2]
            numbers_text = numbers_cell.get_text(strip=True)
            
            # 提取3个0-9的数字
            numbers = []
            # 先尝试提取所有单个数字
            digits = re.findall(r'\d', numbers_text)
            for d in digits:
                num = int(d)
                if 0 <= num <= 9:
                    numbers.append(num)
                    if len(numbers) >= 3:
                        break
            
            if len(numbers) >= 3:
                records.append({
                    'period': period,
                    'numbers': numbers[:3]
                })
    
    return records

def parse_kl8(html, year):
    """解析快乐8数据"""
    records = []
    # 优先使用 lxml，如果失败则使用 html.parser
    try:
        soup = BeautifulSoup(html, 'lxml')
    except:
        soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有表格
    tables = soup.find_all('table')
    seen_periods = set()  # 用于去重
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:  # 至少需要3列：开奖时间、期数、号码
                continue
            
            # 跳过表头
            first_cell_text = cells[0].get_text(strip=True).upper()
            if first_cell_text in ['开奖时间', '期号', '期数', 'PERIOD', '期', '开奖日期']:
                continue
            
            # 提取期号（从第2列，索引1）
            period_text = cells[1].get_text(strip=True)
            # 匹配7位期号（如2026023）或3位期号（如023）
            period_match = re.search(r'(\d{7}|\d{3})', period_text)
            if not period_match:
                continue
            
            period = period_match.group(1)
            if len(period) == 7:
                period = period[-3:]  # 取后3位
            period = period.zfill(3)
            
            # 去重
            if period in seen_periods:
                continue
            seen_periods.add(period)
            
            # 提取号码（从第3列，索引2，即"号码"列）
            numbers_cell = cells[2]
            numbers_text = numbers_cell.get_text(strip=True)
            
            # 提取20个1-80的数字
            numbers = []
            nums = re.findall(r'\d+', numbers_text)
            for n in nums:
                num = int(n)
                if 1 <= num <= 80:
                    numbers.append(num)
                    if len(numbers) >= 20:
                        break
            
            if len(numbers) >= 20:
                # 去重并排序
                numbers = sorted(list(set(numbers[:20])))
                if len(numbers) >= 20:
                    records.append({
                        'period': period,
                        'numbers': numbers[:20]
                    })
    
    return records

def format_ssq_record(record):
    """格式化双色球记录"""
    red_str = ' '.join([f"{n:02d}" for n in record['red']])
    blue_str = f"{record['blue']:02d}"
    return f"第{record['period']}期: {red_str} + {blue_str}"

def format_sd_record(record):
    """格式化3D记录"""
    nums_str = ' '.join([str(n) for n in record['numbers']])
    return f"第{record['period']}期: {nums_str}"

def format_kl8_record(record):
    """格式化快乐8记录"""
    nums = record['numbers']
    # 第一行：前10个号码
    first_line = ' '.join([f"{n:02d}" for n in nums[:10]])
    # 第二行：后10个号码（带缩进）
    second_line = ' '.join([f"{n:02d}" for n in nums[10:20]])
    return f"第{record['period']}期: {first_line}\n        {second_line}"

def get_file_year(output_file):
    """从文件修改时间判断年份"""
    if not os.path.exists(output_file):
        return None
    
    # 使用文件修改时间判断年份
    file_mtime = os.path.getmtime(output_file)
    file_year = datetime.fromtimestamp(file_mtime).year
    return file_year

def save_records(records, output_file, format_func, current_year):
    """保存记录到文件"""
    # 确保目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 如果文件已存在，检查是否是当前年份的数据
    if os.path.exists(output_file):
        file_year = get_file_year(output_file)
        # 如果文件年份不是当前年份，清除文件
        if file_year and file_year < current_year:
            print(f"检测到{file_year}年数据，清除旧数据: {output_file}")
            os.remove(output_file)
    
    # 按期号排序（降序，最新在前）
    records.sort(key=lambda x: int(x['period']), reverse=True)
    
    # 写入文件（覆盖模式，只保存当前年份）
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in records:
            f.write(format_func(record) + '\n')

def fetch_and_save(lottery_type, year):
    """抓取并保存数据"""
    # 先尝试主数据源
    url = URLS[lottery_type].format(year=year)
    print(f"抓取 {lottery_type} {year}年数据: {url}")
    
    html = fetch_page(url)
    
    if not html:
        print(f"抓取失败: {lottery_type}")
        return False
    
    # 解析数据
    if lottery_type == 'ssq':
        records = parse_ssq(html, year)
        format_func = format_ssq_record
    elif lottery_type == 'sd':
        records = parse_sd(html, year)
        format_func = format_sd_record
    elif lottery_type == 'kl8':
        records = parse_kl8(html, year)
        format_func = format_kl8_record
    else:
        return False
    
    if not records:
        print(f"未解析到数据: {lottery_type}")
        return False
    
    # 保存数据
    output_file = OUTPUT_FILES[lottery_type]
    save_records(records, output_file, format_func, year)
    print(f"保存成功: {lottery_type}, 共{len(records)}期")
    return True

def main():
    """主函数"""
    current_year = get_current_year()
    print(f"当前年份: {current_year}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试网络连接
    if not test_connection():
        print("\n警告: 网络连接测试失败，可能无法访问目标网站")
        print("如果是在 GitHub Actions 中运行，可能需要:")
        print("1. 配置代理服务器")
        print("2. 使用本地运行后手动提交数据")
        print("3. 或使用其他可访问的数据源\n")
    
    # 检查并清除旧年份数据
    for lottery_type, output_file in OUTPUT_FILES.items():
        if os.path.exists(output_file):
            file_year = get_file_year(output_file)
            if file_year and file_year < current_year:
                print(f"检测到{file_year}年数据，清除旧数据: {output_file}")
                try:
                    os.remove(output_file)
                except Exception as e:
                    print(f"清除文件失败: {e}")
    
    # 抓取三个彩票的数据
    success_count = 0
    for lottery_type in ['ssq', 'sd', 'kl8']:
        try:
            if fetch_and_save(lottery_type, current_year):
                success_count += 1
            time.sleep(3)  # 避免请求过快
        except Exception as e:
            print(f"处理 {lottery_type} 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"完成: 成功抓取 {success_count}/3 个彩票数据")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 如果全部失败，提供诊断信息
    if success_count == 0:
        print("\n" + "="*60)
        print("诊断信息：")
        print("所有数据源连接失败，可能的原因：")
        print("1. 网络连接问题：请检查网络连接")
        print("2. 网站访问限制：www.55128.cn 可能阻止了当前IP")
        print("3. GitHub Actions 环境限制：")
        print("   - GitHub Actions 服务器可能无法访问某些中国网站")
        print("   - 建议：在本地环境运行脚本，然后手动提交数据")
        print("   - 或者：配置代理服务器（需要设置代理环境变量）")
        print("4. 本地测试：")
        print("   - 在浏览器中访问: https://www.55128.cn/kjh/history_fcssq.aspx?year=2026")
        print("   - 如果浏览器可以访问，但脚本不行，可能是反爬虫机制")
        print("="*60)
    
    return success_count == 3

if __name__ == '__main__':
    main()

