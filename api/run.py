from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import re
import urllib3
import time

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_lottery_data():
    """使用 requests 获取数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # 尝试多次请求
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"尝试第 {attempt + 1} 次请求...")
                response = requests.get(
                    'https://akjw09d.48489aaa.com:8800/',
                    headers=headers,
                    verify=False,
                    timeout=30
                )
                response.raise_for_status()
                print("请求成功")
                print(f"响应长度: {len(response.text)}")
                print(f"响应内容预览: {response.text[:200]}")  # 打印响应内容的前200个字符
                break
            except requests.RequestException as e:
                print(f"请求失败: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        
        print("开始解析HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 打印页面结构
        print("页面结构预览:")
        print(soup.prettify()[:500])  # 打印格式化后的HTML前500个字符
        
        lottery_types = {
            'lam': ('AMLHC2', '老澳门六合彩'),
            'xam': ('AMLHC3', '新澳门六合彩'),
            'hk': ('LHC', '六合彩'),
            'tc': ('TWLHC', '台湾六合彩')
        }
        
        results = {}
        for lottery_id, (code, name) in lottery_types.items():
            try:
                print(f"处理 {name}...")
                # 尝试不同的选择器
                lottery_div = soup.find(id=code) or soup.find('div', {'id': code}) or soup.find('div', {'data-id': code})
                if not lottery_div:
                    print(f"未找到 {name} 区块，尝试其他方法...")
                    # 打印所有div的id
                    all_divs = soup.find_all('div', id=True)
                    print(f"页面中的所有div id: {[div.get('id') for div in all_divs]}")
                    continue
                
                print(f"找到 {name} 区块，内容预览: {lottery_div.prettify()[:200]}")
                    
                issue_element = lottery_div.find(class_="preDrawIssue")
                if not issue_element:
                    print(f"未找到 {name} 期号")
                    continue
                    
                issue_number = issue_element.text.strip()
                match = re.search(r'(\d+)$', issue_number)
                if not match:
                    print(f"{name} 期号格式错误")
                    continue
                issue_short = match.group(1)[-3:]
                
                number_box = lottery_div.find(class_="number-box")
                if not number_box:
                    print(f"未找到 {name} 号码区块")
                    continue
                    
                numbers = []
                special_number = None
                special_zodiac = None
                
                number_elements = [li for li in number_box.find_all('li') 
                                 if 'xgcaddF1' not in li.get('class', [])]
                
                print(f"找到 {len(number_elements)} 个号码元素")
                
                for i, elem in enumerate(number_elements):
                    number = elem.find('span').text.strip().zfill(2)
                    zodiac = elem.find(class_="animal").text.strip()
                    
                    if i == len(number_elements) - 1:
                        special_number = number
                        special_zodiac = zodiac
                    else:
                        numbers.append(number)
                
                if numbers and special_number:
                    result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
                    results[lottery_id] = result
                    print(f"成功获取 {name} 结果")
                    
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                continue
                
        return results
        
    except Exception as e:
        print(f"请求数据时出错: {str(e)}")
        return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print("开始执行爬虫...")
            results = get_lottery_data()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                "status": "success" if results else "error",
                "data": results if results else {},
                "message": "Data fetched successfully" if results else "Failed to fetch data"
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"处理请求时出错: {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "status": "error",
                "error": str(e),
                "message": "Request handler failed"
            }
            
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8')) 