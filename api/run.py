from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib3
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_lottery_data():
    """使用与 scraper.py 相同的方式获取数据"""
    try:
        session = requests.Session()
        session.verify = False
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://akjw09d.48489aaa.com:8800/',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': 'visited=true'
        }
        
        # 首先访问主页获取必要的 cookie
        session.get('https://akjw09d.48489aaa.com:8800/', headers=headers)
        
        # 直接请求API获取数据
        api_url = 'https://akjw09d.48489aaa.com:8800/api/lottery/current'
        response = session.get(api_url, headers=headers)
        
        try:
            data = response.json()
            print("API响应:", data)
            
            lottery_types = {
                'lam': ('AMLHC2', '老澳门六合彩'),
                'xam': ('AMLHC3', '新澳门六合彩'),
                'hk': ('LHC', '六合彩'),
                'tc': ('TWLHC', '台湾六合彩')
            }
            
            results = {}
            for lottery_id, (code, name) in lottery_types.items():
                try:
                    if code in data:
                        lottery_data = data[code]
                        issue = lottery_data.get('issue', '')
                        numbers = lottery_data.get('numbers', [])
                        special = lottery_data.get('special', {})
                        
                        if issue and numbers and special:
                            issue_short = issue[-3:]
                            result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special['number']} {special['zodiac']}"
                            results[lottery_id] = result
                            print(f"成功获取 {name} 结果: {result}")
                            
                except Exception as e:
                    print(f"处理 {name} 数据时出错: {str(e)}")
                    continue
                    
            return results
            
        except ValueError:
            print("API返回非JSON数据，尝试解析HTML...")
            # 如果API请求失败，尝试解析HTML
            response = session.get(
                'https://akjw09d.48489aaa.com:8800/lottery/results',
                headers=headers
            )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = {}
            for lottery_id, (code, name) in lottery_types.items():
                try:
                    lottery_div = soup.find('div', {'data-lottery': code})
                    if not lottery_div:
                        continue
                        
                    issue_element = lottery_div.find(class_="issue")
                    if not issue_element:
                        continue
                        
                    issue_number = issue_element.text.strip()
                    match = re.search(r'(\d+)$', issue_number)
                    if not match:
                        continue
                    issue_short = match.group(1)[-3:]
                    
                    numbers_div = lottery_div.find(class_="numbers")
                    if not numbers_div:
                        continue
                        
                    number_elements = numbers_div.find_all(class_="number")
                    
                    numbers = []
                    special_number = None
                    special_zodiac = None
                    
                    for i, elem in enumerate(number_elements):
                        number = elem.text.strip().zfill(2)
                        zodiac = elem.find_next(class_="zodiac").text.strip()
                        
                        if i == len(number_elements) - 1:
                            special_number = number
                            special_zodiac = zodiac
                        else:
                            numbers.append(number)
                    
                    if numbers and special_number:
                        results[lottery_id] = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
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
        finally:
            if 'driver' in locals():
                try:
                    driver.quit()
                    print("浏览器已关闭")
                except Exception as e:
                    print(f"关闭浏览器时出错: {str(e)}") 