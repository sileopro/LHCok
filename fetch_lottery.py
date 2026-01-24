#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票数据抓取脚本
从 datachart.500.com 抓取双色球、3D、快乐8的历史开奖数据
参考 lotteryhistorygrabber.py 的实现
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import time

# 数据源URL（参考 lotteryhistorygrabber.py）
# 使用 history.php 接口获取数据
URLS = {
    'ssq': 'http://datachart.500.com/ssq/history/newinc/history.php',
    'sd': 'http://datachart.500.com/sd/history/newinc/history.php',
    'kl8': 'http://datachart.500.com/kl8/history/newinc/history.php'
}

# 输出文件路径
OUTPUT_DIR = 'fc'
OUTPUT_FILES = {
    'ssq': os.path.join(OUTPUT_DIR, 'ssq.txt'),
    'sd': os.path.join(OUTPUT_DIR, 'sd.txt'),
    'kl8': os.path.join(OUTPUT_DIR, 'kl8.txt')
}

# 请求头（参考 lotteryhistorygrabber.py）
HEADERS = {
    'Host': 'datachart.500.com',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'http://datachart.500.com/ssq/history/history.shtml',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}


def get_current_year():
    """获取当前年份"""
    return datetime.now().year


def fetch_page(url, params=None, retry=3):
    """抓取网页内容（参考 lotteryhistorygrabber.py 的 getHtml）"""
    for attempt in range(retry):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"HTTP错误 {response.status_code} (尝试 {attempt + 1}/{retry})")
        except requests.exceptions.RequestException as e:
            print(f"请求失败 (尝试 {attempt + 1}/{retry}): {e}")
        
        if attempt < retry - 1:
            time.sleep(2)
    
    return None


def parse_ssq(html):
    """解析双色球数据（参考 lotteryhistorygrabber.py 的 Parser500ssq）
    从 tbody#tdata 中提取数据
    """
    records = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找 id="tdata" 的 tbody（参考 lotteryhistorygrabber.py）
        tbody = soup.find('tbody', id='tdata')
        if not tbody:
            tbody = soup.find('tbody')
        
        if not tbody:
            print("双色球: 未找到数据表格")
            return records
        
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 8:  # 至少需要：期号 + 7个号码
                continue
            
            # 第一列是期号
            period_text = cells[0].get_text(strip=True)
            period_match = re.search(r'(\d{7}|\d{3})', period_text)
            if not period_match:
                continue
            
            period_full = period_match.group(1)
            if len(period_full) == 7:
                year = period_full[:4]
                period = period_full[4:]
            else:
                year = str(get_current_year())
                period = period_full.zfill(3)
            
            # 提取号码：红球在第2-7列，蓝球在第8列
            numbers = []
            for i in range(1, 8):
                if i < len(cells):
                    num_text = cells[i].get_text(strip=True)
                    try:
                        num = int(num_text)
                        numbers.append(num)
                    except ValueError:
                        continue
            
            # 验证：6个红球(1-33) + 1个蓝球(1-16)
            if len(numbers) == 7:
                reds = numbers[:6]
                blue = numbers[6]
                if all(1 <= r <= 33 for r in reds) and 1 <= blue <= 16:
                    records.append({
                        'year': year,
                        'period': period,
                        'numbers': sorted(reds) + [blue]
                    })
        
        print(f"双色球: 解析到 {len(records)} 条记录")
        return records
        
    except Exception as e:
        print(f"双色球解析错误: {e}")
        return records


def parse_sd(html):
    """解析3D数据"""
    records = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        tbody = soup.find('tbody', id='tdata')
        if not tbody:
            tbody = soup.find('tbody')
        
        if not tbody:
            print("3D: 未找到数据表格")
            return records
        
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 4:  # 至少需要：期号 + 3个号码
                continue
            
            # 第一列是期号
            period_text = cells[0].get_text(strip=True)
            period_match = re.search(r'(\d{7}|\d{3})', period_text)
            if not period_match:
                continue
            
            period_full = period_match.group(1)
            if len(period_full) == 7:
                year = period_full[:4]
                period = period_full[4:]
            else:
                year = str(get_current_year())
                period = period_full.zfill(3)
            
            # 提取号码：3个数字(0-9)
            numbers = []
            for i in range(1, 4):
                if i < len(cells):
                    num_text = cells[i].get_text(strip=True)
                    try:
                        num = int(num_text)
                        if 0 <= num <= 9:
                            numbers.append(num)
                    except ValueError:
                        continue
            
            # 验证：3个数字(0-9)
            if len(numbers) == 3:
                records.append({
                    'year': year,
                    'period': period,
                    'numbers': numbers
                })
        
        print(f"3D: 解析到 {len(records)} 条记录")
        return records
        
    except Exception as e:
        print(f"3D解析错误: {e}")
        return records


def parse_kl8(html):
    """解析快乐8数据"""
    records = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        tbody = soup.find('tbody', id='tdata')
        if not tbody:
            tbody = soup.find('tbody')
        
        if not tbody:
            print("快乐8: 未找到数据表格")
            return records
        
        rows = tbody.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 21:  # 至少需要：期号 + 20个号码
                continue
            
            # 第一列是期号
            period_text = cells[0].get_text(strip=True)
            period_match = re.search(r'(\d{7}|\d{3})', period_text)
            if not period_match:
                continue
            
            period_full = period_match.group(1)
            if len(period_full) == 7:
                year = period_full[:4]
                period = period_full[4:]
            else:
                year = str(get_current_year())
                period = period_full.zfill(3)
            
            # 提取号码：20个数字(1-80)
            numbers = []
            for i in range(1, 21):
                if i < len(cells):
                    num_text = cells[i].get_text(strip=True)
                    try:
                        num = int(num_text)
                        if 1 <= num <= 80:
                            numbers.append(num)
                    except ValueError:
                        continue
            
            # 验证：20个不重复的数字(1-80)
            if len(numbers) == 20 and len(set(numbers)) == 20:
                records.append({
                    'year': year,
                    'period': period,
                    'numbers': sorted(numbers)
                })
        
        print(f"快乐8: 解析到 {len(records)} 条记录")
        return records
        
    except Exception as e:
        print(f"快乐8解析错误: {e}")
        return records


def format_ssq_record(record):
    """格式化双色球记录
    格式: 第xxx期: 01 02 03 04 05 06 + 07
    """
    period = record['period']
    numbers = record['numbers']
    reds = ' '.join(str(n).zfill(2) for n in numbers[:6])
    blue = str(numbers[6]).zfill(2)
    return f"第{period}期: {reds} + {blue}"


def format_sd_record(record):
    """格式化3D记录
    格式: 第xxx期: 1 2 3
    """
    period = record['period']
    numbers = record['numbers']
    nums_str = ' '.join(str(n) for n in numbers)
    return f"第{period}期: {nums_str}"


def format_kl8_record(record):
    """格式化快乐8记录
    格式: 第xxx期: 01 02 03 04 05 06 07 08 09 10
                  11 12 13 14 15 16 17 18 19 20
    """
    period = record['period']
    numbers = record['numbers']
    first_row = ' '.join(str(n).zfill(2) for n in numbers[:10])
    second_row = ' '.join(str(n).zfill(2) for n in numbers[10:])
    return f"第{period}期: {first_row}\n          {second_row}"


def get_file_year(filepath):
    """从文件中获取已保存数据的年份"""
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line:
                match = re.search(r'#\s*(\d{4})', first_line)
                if match:
                    return match.group(1)
    except:
        pass
    
    return None


def save_records(lottery_type, records):
    """保存所有记录到文件
    
    规则：
    1. 保存当前年份的所有期数
    2. 如果最新一期是下一年的，清除上一年的数据，只保存新年的数据
    """
    if not records:
        return False
    
    # 确保目录存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    output_file = OUTPUT_FILES[lottery_type]
    lottery_names = {'ssq': '双色球', 'sd': '3D', 'kl8': '快乐8'}
    
    # 找出最新一期的年份
    latest_year = None
    for record in records:
        if latest_year is None or int(record['year']) > int(latest_year):
            latest_year = record['year']
    
    if not latest_year:
        return False
    
    # 检查文件中已保存的年份
    existing_year = get_file_year(output_file)
    
    # 如果年份变了，只保存新年份的数据
    if existing_year and existing_year != latest_year:
        print(f"{lottery_type}: 年份变更 {existing_year} -> {latest_year}，清空旧数据")
    
    # 只保存最新年份的记录
    year_records = [r for r in records if r['year'] == latest_year]
    
    # 按期号排序
    year_records.sort(key=lambda x: int(x['period']))
    
    # 去重
    seen_periods = set()
    unique_records = []
    for record in year_records:
        if record['period'] not in seen_periods:
            seen_periods.add(record['period'])
            unique_records.append(record)
    
    # 格式化记录
    if lottery_type == 'ssq':
        format_func = format_ssq_record
    elif lottery_type == 'sd':
        format_func = format_sd_record
    elif lottery_type == 'kl8':
        format_func = format_kl8_record
    else:
        return False
    
    # 写入文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {latest_year}年{lottery_names[lottery_type]}开奖记录\n")
            for record in unique_records:
                f.write(format_func(record) + '\n')
        
        print(f"{lottery_type}: 保存 {len(unique_records)} 条 {latest_year}年 记录")
        return True
        
    except Exception as e:
        print(f"{lottery_type}: 保存失败 - {e}")
        return False


def fetch_and_save(lottery_type):
    """抓取并保存数据"""
    url = URLS[lottery_type]
    lottery_names = {'ssq': '双色球', 'sd': '3D', 'kl8': '快乐8'}
    
    # 设置查询参数（获取当前年份的所有数据）
    current_year = get_current_year()
    # start=1 表示从第1期开始，end=年份999 表示到该年份最后一期
    params = {
        'start': '1',
        'end': f'{current_year}999'
    }
    
    # 更新 Referer
    referers = {
        'ssq': 'http://datachart.500.com/ssq/history/history.shtml',
        'sd': 'http://datachart.500.com/sd/history/history.shtml',
        'kl8': 'http://datachart.500.com/kl8/history/history.shtml'
    }
    HEADERS['Referer'] = referers.get(lottery_type, HEADERS['Referer'])
    
    print(f"\n抓取 {lottery_names[lottery_type]}: {url}")
    print(f"参数: start={params['start']}, end={params['end']}")
    
    html = fetch_page(url, params=params)
    
    if not html:
        print(f"{lottery_type}: 抓取失败")
        return False
    
    print(f"{lottery_type}: 获取到HTML，长度 {len(html)}")
    
    # 解析数据
    if lottery_type == 'ssq':
        records = parse_ssq(html)
    elif lottery_type == 'sd':
        records = parse_sd(html)
    elif lottery_type == 'kl8':
        records = parse_kl8(html)
    else:
        records = []
    
    if not records:
        print(f"{lottery_type}: 解析失败，未获取到有效数据")
        return False
    
    # 保存数据
    return save_records(lottery_type, records)


def main():
    """主函数"""
    print("=" * 50)
    print(f"彩票数据抓取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("数据源: datachart.500.com")
    print("=" * 50)
    
    success_count = 0
    lottery_types = ['ssq', 'sd', 'kl8']
    
    for lottery_type in lottery_types:
        try:
            if fetch_and_save(lottery_type):
                success_count += 1
        except Exception as e:
            print(f"{lottery_type}: 处理异常 - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"完成: 成功处理 {success_count}/{len(lottery_types)} 个彩票数据")
    print("=" * 50)
    
    # 列出生成的文件
    if os.path.exists(OUTPUT_DIR):
        print(f"\n生成的文件:")
        for f in os.listdir(OUTPUT_DIR):
            filepath = os.path.join(OUTPUT_DIR, f)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                print(f"  {f}: {size} bytes")


if __name__ == '__main__':
    main()
