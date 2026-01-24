#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票数据抓取脚本
参考 ssqiu.js, sand.js, kuaileba.js 的抓取逻辑
从 www.cjcp.cn 抓取双色球、3D、快乐8的最新开奖数据
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import time

# 数据源URL（与JS文件保持一致）
URLS = {
    'ssq': 'https://www.cjcp.cn/kaijiang/ssq/',      # 双色球
    'sd': 'https://www.cjcp.cn/kaijiang/3d/',        # 3D
    'kl8': 'https://www.cjcp.cn/kaijiang/fckl8/'     # 快乐8
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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'no-cache'
}


def get_current_year():
    """获取当前年份"""
    return datetime.now().year


def fetch_page(url, retry=3):
    """抓取网页内容"""
    # 添加时间戳参数，避免缓存（参考JS文件）
    url_with_ts = url + ('&' if '?' in url else '?') + '_t=' + str(int(time.time() * 1000))
    
    for attempt in range(retry):
        try:
            response = requests.get(url_with_ts, headers=HEADERS, timeout=30)
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


def is_valid_ssq_numbers(numbers):
    """验证双色球号码是否有效（参考 ssqiu.js 的 isValidSSQNumbers）
    6个红球(1-33) + 1个蓝球(1-16)
    """
    if not isinstance(numbers, list) or len(numbers) != 7:
        return False
    # 前6个是红球(1-33)
    for i in range(6):
        if not isinstance(numbers[i], int) or numbers[i] < 1 or numbers[i] > 33:
            return False
    # 第7个是蓝球(1-16)
    if not isinstance(numbers[6], int) or numbers[6] < 1 or numbers[6] > 16:
        return False
    return True


def is_valid_3d_numbers(numbers):
    """验证3D号码是否有效（参考 sand.js 的 isValid3DNumbers）
    3个数字(0-9)
    """
    if not isinstance(numbers, list) or len(numbers) != 3:
        return False
    for n in numbers:
        if not isinstance(n, int) or n < 0 or n > 9:
            return False
    return True


def is_valid_kl8_numbers(numbers):
    """验证快乐8号码是否有效（参考 kuaileba.js 的 validateNumbers）
    20个不重复的数字(1-80)
    """
    if not isinstance(numbers, list) or len(numbers) != 20:
        return False
    for n in numbers:
        if not isinstance(n, int) or n < 1 or n > 80:
            return False
    # 检查是否有重复
    if len(set(numbers)) != 20:
        return False
    return True


def is_invalid_ball_text(text):
    """检查是否是无效的号码球文本（参考 kuaileba.js）
    开奖时可能显示 "-"、"—"、"－"、"−" 等占位符
    """
    if not text:
        return True
    text = text.strip()
    if not text:
        return True
    # 检查是否是各种横线符号
    invalid_chars = ['-', '—', '－', '−', '–', '―']
    if text in invalid_chars:
        return True
    # 检查是否全是横线符号
    if re.match(r'^[\s\-—－−–―]+$', text):
        return True
    return False


def parse_ssq(html):
    """解析双色球数据（参考 ssqiu.js 的 parseLatestSSQFromHtml）"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找候选容器（参考JS的candidateSelectors）
        candidate_selectors = [
            '.kj_num',
            '.kj_num_box',
            '.kj_num_list',
            'div[class*="kj"]',
            'div[class*="num"]'
        ]
        
        container = None
        for selector in candidate_selectors:
            nodes = soup.select(selector)
            for node in nodes:
                text = node.get_text(strip=True)
                if not text:
                    continue
                # 检查是否包含期号信息
                if '期' in text or re.search(r'\d{4}\d{3}', text) or re.search(r'\d{1,4}期', text):
                    # 查找红球和蓝球
                    red_balls = node.select('span.qiu_red, span[class*="red"], span[class*="ball_red"], i.red, em.red')
                    blue_balls = node.select('span.qiu_blue, span[class*="blue"], span[class*="ball_blue"], i.blue, em.blue')
                    
                    reds = []
                    for ball in red_balls:
                        t = ball.get_text(strip=True)
                        if is_invalid_ball_text(t):
                            continue
                        try:
                            num = int(t)
                            if 1 <= num <= 33:
                                reds.append(num)
                        except ValueError:
                            continue
                    
                    blues = []
                    for ball in blue_balls:
                        t = ball.get_text(strip=True)
                        if is_invalid_ball_text(t):
                            continue
                        try:
                            num = int(t)
                            if 1 <= num <= 16:
                                blues.append(num)
                        except ValueError:
                            continue
                    
                    if len(reds) >= 6 and len(blues) >= 1:
                        container = node
                        break
            if container:
                break
        
        # 提取期号
        text_for_period = container.get_text() if container else html
        text_for_period = re.sub(r'\s+', ' ', text_for_period)
        
        year = None
        period = None
        
        # 优先匹配 2026009 格式
        match_full = re.search(r'(20\d{2})(\d{3})', text_for_period)
        if match_full:
            year = match_full.group(1)
            period = match_full.group(2)
        else:
            # 尝试匹配 "第xxx期" 格式
            match_period = re.search(r'第\s*(\d{1,4})\s*期', text_for_period)
            if match_period:
                period = match_period.group(1)
            match_year = re.search(r'(20\d{2})', text_for_period)
            year = match_year.group(1) if match_year else str(get_current_year())
        
        if not year or not period:
            print("双色球: 未找到期号")
            return None
        
        # 标准化期号为3位
        period = period.zfill(3)
        if period == '000' or int(period) == 0:
            print("双色球: 期号无效")
            return None
        
        # 提取号码
        numbers = []
        if container:
            red_balls = container.select('span.qiu_red, span[class*="red"], span[class*="ball_red"], i.red, em.red')
            blue_balls = container.select('span.qiu_blue, span[class*="blue"], span[class*="ball_blue"], i.blue, em.blue')
            
            reds = []
            for ball in red_balls:
                t = ball.get_text(strip=True)
                if is_invalid_ball_text(t):
                    print(f"双色球: 发现无效红球 '{t}'，号码不完整")
                    return None
                try:
                    num = int(t)
                    if 1 <= num <= 33:
                        reds.append(num)
                except ValueError:
                    continue
            
            blues = []
            for ball in blue_balls:
                t = ball.get_text(strip=True)
                if is_invalid_ball_text(t):
                    print(f"双色球: 发现无效蓝球 '{t}'，号码不完整")
                    return None
                try:
                    num = int(t)
                    if 1 <= num <= 16:
                        blues.append(num)
                except ValueError:
                    continue
            
            if len(reds) >= 6 and len(blues) >= 1:
                numbers = sorted(reds[:6]) + [blues[0]]
        
        # 验证号码
        if not is_valid_ssq_numbers(numbers):
            print(f"双色球: 号码不完整或无效 (红球: {len(reds) if 'reds' in dir() else 0}, 蓝球: {len(blues) if 'blues' in dir() else 0})")
            return None
        
        return {
            'year': year,
            'period': period,
            'numbers': numbers
        }
        
    except Exception as e:
        print(f"双色球解析错误: {e}")
        return None


def parse_sd(html):
    """解析3D数据（参考 sand.js 的 parseLatest3DFromHtml）"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找候选容器
        candidate_selectors = [
            '.kj_num',
            '.kj_num_box',
            '.kj_num_list',
            'div[class*="kj"]',
            'div[class*="num"]'
        ]
        
        container = None
        for selector in candidate_selectors:
            nodes = soup.select(selector)
            for node in nodes:
                text = node.get_text(strip=True)
                if not text:
                    continue
                # 3D页面通常包含"期"字或期号信息
                if '期' in text or re.search(r'\d{4}\d{3}', text) or re.search(r'\d{1,4}期', text):
                    # 找里面的球元素
                    balls = node.select('span.qiu_red, span[class*="red"], span[class*="ball"], [class*="qiu"], i, em')
                    digits = []
                    for ball in balls:
                        t = ball.get_text(strip=True)
                        if is_invalid_ball_text(t):
                            continue
                        if re.match(r'^\d$', t):
                            digits.append(int(t))
                    
                    if len(digits) >= 3:
                        container = node
                        break
            if container:
                break
        
        # 如果没找到容器，尝试全页面找
        digits_fallback = []
        if not container:
            all_spans = soup.select('span, i, em, b')
            for el in all_spans:
                t = el.get_text(strip=True)
                if is_invalid_ball_text(t):
                    continue
                if re.match(r'^\d$', t):
                    digits_fallback.append(int(t))
                    if len(digits_fallback) >= 3:
                        break
        
        # 提取期号
        text_for_period = container.get_text() if container else html
        text_for_period = re.sub(r'\s+', ' ', text_for_period)
        
        year = None
        period = None
        
        match_full = re.search(r'(20\d{2})(\d{3})', text_for_period)
        if match_full:
            year = match_full.group(1)
            period = match_full.group(2)
        else:
            match_period = re.search(r'第\s*(\d{1,4})\s*期', text_for_period)
            if match_period:
                period = match_period.group(1)
            match_year = re.search(r'(20\d{2})', text_for_period)
            year = match_year.group(1) if match_year else str(get_current_year())
        
        if not year or not period:
            print("3D: 未找到期号")
            return None
        
        period = period.zfill(3)
        if period == '000' or int(period) == 0:
            print("3D: 期号无效")
            return None
        
        # 提取号码
        numbers = []
        if container:
            balls = container.select('span.qiu_red, span[class*="red"], span[class*="ball"], [class*="qiu"], i, em')
            for ball in balls:
                t = ball.get_text(strip=True)
                if is_invalid_ball_text(t):
                    print(f"3D: 发现无效号码 '{t}'，号码不完整")
                    return None
                if re.match(r'^\d$', t):
                    numbers.append(int(t))
                    if len(numbers) >= 3:
                        break
        else:
            numbers = digits_fallback[:3]
        
        # 验证号码
        if not is_valid_3d_numbers(numbers):
            print(f"3D: 号码不完整或无效 (找到 {len(numbers)} 个)")
            return None
        
        return {
            'year': year,
            'period': period,
            'numbers': numbers
        }
        
    except Exception as e:
        print(f"3D解析错误: {e}")
        return None


def parse_kl8(html):
    """解析快乐8数据（参考 kuaileba.js 的 parseLatestFromHtml）"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 方案1：查找 class="kb_num kj_num public_num" 的元素（m.ssqzj.com风格）
        public_num_results = soup.select('div.kb_num.kj_num.public_num')
        if public_num_results:
            result = public_num_results[0]
            period_text = result.get_text(strip=True)
            period_match = re.search(r'第(\d+)期', period_text)
            
            if period_match:
                period_num = period_match.group(1)
                number_spans = result.select('span.qiu_red')
                
                # 检查号码球数量
                if len(number_spans) < 20:
                    print(f"快乐8: 号码球元素不足20个 ({len(number_spans)})")
                else:
                    number_list = []
                    for span in number_spans:
                        t = span.get_text(strip=True)
                        if is_invalid_ball_text(t):
                            print(f"快乐8: 发现无效号码 '{t}'，号码不完整")
                            number_list = []
                            break
                        try:
                            num = int(t)
                            if 1 <= num <= 80 and num not in number_list:
                                number_list.append(num)
                        except ValueError:
                            continue
                    
                    if len(number_list) == 20:
                        year_match = re.search(r'(\d{4})', period_text)
                        year = year_match.group(1) if year_match else str(get_current_year())
                        period = period_num.zfill(3)
                        numbers = sorted(number_list)
                        
                        if is_valid_kl8_numbers(numbers):
                            return {
                                'year': year,
                                'period': period,
                                'numbers': numbers
                            }
        
        # 方案2：通用容器查找
        candidate_selectors = [
            'div.kj_num',
            'div.kb_num',
            '.kj_num_box',
            '.kj_num_list',
            '[class*="kj"]',
            '[class*="num"]'
        ]
        
        container = None
        for selector in candidate_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text() or ''
                if '开奖号' in text or '期' in text or re.search(r'\d{7}', text):
                    red_balls = elem.select('span.qiu_red, span[class*="red"], span[class*="ball"], .qiu_red, [class*="qiu"]')
                    if len(red_balls) >= 20:
                        container = elem
                        break
            if container:
                break
        
        if container:
            # 提取期号
            period_text = ''
            search_elem = container
            for _ in range(5):
                period_text = search_elem.get_text() or ''
                if re.search(r'\d{7}', period_text) or re.search(r'第\d+期', period_text) or '开奖号' in period_text:
                    break
                search_elem = search_elem.parent
                if not search_elem:
                    break
            
            # 提取期号
            period_match = re.search(r'(\d{4})(\d{3})', period_text)
            year = None
            period = None
            
            if period_match:
                year = period_match.group(1)
                period = period_match.group(2)
            else:
                period_match2 = re.search(r'第(\d+)期', period_text)
                if period_match2:
                    period = period_match2.group(1)
                year_match = re.search(r'(\d{4})', period_text)
                year = year_match.group(1) if year_match else str(get_current_year())
            
            if not year or not period:
                print("快乐8: 未找到期号")
                return None
            
            period = period.zfill(3)
            if period == '000' or int(period) == 0:
                print("快乐8: 期号无效")
                return None
            
            # 提取号码
            number_spans = container.select('span.qiu_red, span[class*="red"], span[class*="ball"], .qiu_red, [class*="qiu"]')
            
            if len(number_spans) < 20:
                print(f"快乐8: 号码球元素不足20个 ({len(number_spans)})")
                return None
            
            number_list = []
            for span in number_spans:
                t = span.get_text(strip=True)
                if is_invalid_ball_text(t):
                    print(f"快乐8: 发现无效号码 '{t}'，号码不完整")
                    return None
                try:
                    num = int(t)
                    if 1 <= num <= 80 and num not in number_list:
                        number_list.append(num)
                        if len(number_list) == 20:
                            break
                except ValueError:
                    continue
            
            if not is_valid_kl8_numbers(number_list):
                print(f"快乐8: 号码不完整或无效 (找到 {len(number_list)} 个)")
                return None
            
            return {
                'year': year,
                'period': period,
                'numbers': sorted(number_list)
            }
        
        print("快乐8: 未找到有效的开奖容器")
        return None
        
    except Exception as e:
        print(f"快乐8解析错误: {e}")
        return None


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
                # 尝试从内容中提取年份信息
                match = re.search(r'#\s*(\d{4})', first_line)
                if match:
                    return int(match.group(1))
    except:
        pass
    
    return None


def save_record(lottery_type, record):
    """保存单条记录到文件"""
    if not record:
        return False
    
    # 确保目录存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    output_file = OUTPUT_FILES[lottery_type]
    year = record['year']
    period = record['period']
    
    # 格式化记录
    if lottery_type == 'ssq':
        formatted = format_ssq_record(record)
    elif lottery_type == 'sd':
        formatted = format_sd_record(record)
    elif lottery_type == 'kl8':
        formatted = format_kl8_record(record)
    else:
        return False
    
    # 读取现有记录
    existing_records = []
    existing_year = None
    
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 检查文件头中的年份
                year_match = re.search(r'#\s*(\d{4})年', content)
                if year_match:
                    existing_year = year_match.group(1)
                
                # 提取现有期号
                for line in content.split('\n'):
                    if line.startswith('第'):
                        period_match = re.search(r'第(\d+)期', line)
                        if period_match:
                            existing_records.append(period_match.group(1))
        except:
            pass
    
    # 如果年份变了，清空文件
    if existing_year and existing_year != year:
        print(f"{lottery_type}: 年份变更 {existing_year} -> {year}，清空旧数据")
        existing_records = []
    
    # 检查是否已存在该期
    if period in existing_records:
        print(f"{lottery_type}: 第{period}期已存在，跳过")
        return False
    
    # 写入文件
    try:
        # 如果是新文件或年份变更，写入文件头
        if not existing_records:
            with open(output_file, 'w', encoding='utf-8') as f:
                lottery_names = {'ssq': '双色球', 'sd': '3D', 'kl8': '快乐8'}
                f.write(f"# {year}年{lottery_names[lottery_type]}开奖记录\n")
                f.write(formatted + '\n')
        else:
            # 追加记录
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(formatted + '\n')
        
        print(f"{lottery_type}: 保存第{period}期成功")
        return True
        
    except Exception as e:
        print(f"{lottery_type}: 保存失败 - {e}")
        return False


def fetch_and_save(lottery_type):
    """抓取并保存数据"""
    url = URLS[lottery_type]
    lottery_names = {'ssq': '双色球', 'sd': '3D', 'kl8': '快乐8'}
    print(f"\n抓取 {lottery_names[lottery_type]}: {url}")
    
    html = fetch_page(url)
    
    if not html:
        print(f"{lottery_type}: 抓取失败")
        return False
    
    print(f"{lottery_type}: 获取到HTML，长度 {len(html)}")
    
    # 解析数据
    if lottery_type == 'ssq':
        record = parse_ssq(html)
    elif lottery_type == 'sd':
        record = parse_sd(html)
    elif lottery_type == 'kl8':
        record = parse_kl8(html)
    else:
        record = None
    
    if not record:
        print(f"{lottery_type}: 解析失败或号码不完整（可能正在开奖中）")
        return False
    
    print(f"{lottery_type}: 解析成功 - {record['year']}年第{record['period']}期")
    
    # 保存数据
    return save_record(lottery_type, record)


def main():
    """主函数"""
    print("=" * 50)
    print(f"彩票数据抓取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("数据源: www.cjcp.cn")
    print("=" * 50)
    
    success_count = 0
    lottery_types = ['ssq', 'sd', 'kl8']
    
    for lottery_type in lottery_types:
        try:
            if fetch_and_save(lottery_type):
                success_count += 1
        except Exception as e:
            print(f"{lottery_type}: 处理异常 - {e}")
    
    print("\n" + "=" * 50)
    print(f"完成: 成功处理 {success_count}/{len(lottery_types)} 个彩票数据")
    print("=" * 50)


if __name__ == '__main__':
    main()
