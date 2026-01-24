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

# 网站URL模板
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

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_current_year():
    """获取当前年份"""
    return datetime.now().year

def fetch_page(url, retry=3):
    """抓取网页内容，支持重试"""
    for attempt in range(retry):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"HTTP错误 {response.status_code}: {url}")
        except Exception as e:
            print(f"抓取失败 (尝试 {attempt + 1}/{retry}) {url}: {e}")
            if attempt < retry - 1:
                time.sleep(2)  # 重试前等待
    return None

def parse_ssq(html, year):
    """解析双色球数据"""
    records = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有表格
    tables = soup.find_all('table')
    seen_periods = set()  # 用于去重
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            # 跳过表头
            first_cell_text = cells[0].get_text(strip=True).upper()
            if first_cell_text in ['期号', '期数', 'PERIOD', '期', '开奖日期']:
                continue
            
            # 提取期号（从第一个单元格）
            period_text = cells[0].get_text(strip=True)
            period_match = re.search(r'(\d{3,4})', period_text)
            if not period_match:
                continue
            
            period = period_match.group(1)
            if len(period) > 3:
                period = period[-3:]  # 取后3位
            period = period.zfill(3)
            
            # 去重
            if period in seen_periods:
                continue
            seen_periods.add(period)
            
            # 提取号码（从后续单元格）
            all_numbers = []
            for cell in cells[1:]:
                cell_text = cell.get_text(strip=True)
                # 提取所有数字
                nums = re.findall(r'\d+', cell_text)
                for n in nums:
                    num = int(n)
                    if 1 <= num <= 33:  # 红球范围
                        all_numbers.append(num)
                    elif 1 <= num <= 16:  # 蓝球范围
                        all_numbers.append(num)
            
            # 双色球：6个红球(1-33) + 1个蓝球(1-16)
            red_balls = [n for n in all_numbers if 1 <= n <= 33]
            blue_balls = [n for n in all_numbers if 1 <= n <= 16]
            
            # 去重红球和蓝球
            red_balls = sorted(list(set(red_balls)))
            blue_balls = sorted(list(set(blue_balls)))
            
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
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有表格
    tables = soup.find_all('table')
    seen_periods = set()  # 用于去重
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            # 跳过表头
            first_cell_text = cells[0].get_text(strip=True).upper()
            if first_cell_text in ['期号', '期数', 'PERIOD', '期', '开奖日期']:
                continue
            
            # 提取期号
            period_text = cells[0].get_text(strip=True)
            period_match = re.search(r'(\d{3,4})', period_text)
            if not period_match:
                continue
            
            period = period_match.group(1)
            if len(period) > 3:
                period = period[-3:]  # 取后3位
            period = period.zfill(3)
            
            # 去重
            if period in seen_periods:
                continue
            seen_periods.add(period)
            
            # 提取号码（3D是3个0-9的数字）
            numbers = []
            for cell in cells[1:]:
                cell_text = cell.get_text(strip=True)
                # 提取单个数字
                nums = re.findall(r'\d', cell_text)
                for n in nums:
                    num = int(n)
                    if 0 <= num <= 9:
                        numbers.append(num)
                        if len(numbers) >= 3:
                            break
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
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有表格
    tables = soup.find_all('table')
    seen_periods = set()  # 用于去重
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
            
            # 跳过表头
            first_cell_text = cells[0].get_text(strip=True).upper()
            if first_cell_text in ['期号', '期数', 'PERIOD', '期', '开奖日期']:
                continue
            
            # 提取期号
            period_text = cells[0].get_text(strip=True)
            period_match = re.search(r'(\d{3,4})', period_text)
            if not period_match:
                continue
            
            period = period_match.group(1)
            if len(period) > 3:
                period = period[-3:]  # 取后3位
            period = period.zfill(3)
            
            # 去重
            if period in seen_periods:
                continue
            seen_periods.add(period)
            
            # 提取号码（快乐8是20个1-80的数字）
            numbers = []
            for cell in cells[1:]:
                cell_text = cell.get_text(strip=True)
                nums = re.findall(r'\d+', cell_text)
                for n in nums:
                    num = int(n)
                    if 1 <= num <= 80:
                        numbers.append(num)
                        if len(numbers) >= 20:
                            break
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
    return success_count == 3

if __name__ == '__main__':
    main()

