from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_lottery_data():
    """使用与 scraper.py 相同的方式获取数据"""
    try:
        session = requests.Session()
        session.verify = False
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        
        response = session.get(
            'https://akjw09d.48489aaa.com:8800/',
            headers=headers,
            timeout=30
        )
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        lottery_types = {
            'lam': ('AMLHC2', '老澳门六合彩'),
            'xam': ('AMLHC3', '新澳门六合彩'),
            'hk': ('LHC', '六合彩'),
            'tc': ('TWLHC', '台湾六合彩')
        }
        
        results = {}
        for lottery_id, (code, name) in lottery_types.items():
            try:
                # 使用与 scraper.py 相同的选择器
                lottery_div = soup.find('div', id=code)
                if not lottery_div:
                    print(f"未找到彩票区块: {code}")
                    continue
                
                # 获取期号
                issue_element = lottery_div.find(class_="preDrawIssue")
                if not issue_element:
                    print(f"未找到期号元素")
                    continue
                    
                issue_number = issue_element.text.strip()
                match = re.search(r'(\d+)$', issue_number)
                if not match:
                    print(f"无法从 {issue_number} 提取期号")
                    continue
                issue_short = match.group(1)[-3:]
                
                # 获取号码
                number_box = lottery_div.find(class_="number-box")
                if not number_box:
                    print(f"未找到号码区块")
                    continue
                    
                number_elements = [li for li in number_box.find_all('li') 
                                 if 'xgcaddF1' not in li.get('class', [])]
                
                numbers = []
                special_number = None
                special_zodiac = None
                
                for i, elem in enumerate(number_elements):
                    try:
                        number = elem.find('span').text.strip().zfill(2)
                        zodiac = elem.find(class_="animal").text.strip()
                        
                        if i == len(number_elements) - 1:
                            special_number = number
                            special_zodiac = zodiac
                        else:
                            numbers.append(number)
                    except Exception as e:
                        print(f"处理单个号码时出错: {str(e)}")
                        continue
                
                if numbers and special_number:
                    result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
                    results[lottery_id] = result
                    print(f"成功获取 {name} 结果: {result}")
                else:
                    print(f"号码数据不完整: numbers={numbers}, special_number={special_number}")
                    
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