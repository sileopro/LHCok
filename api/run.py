from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import requests
from bs4 import BeautifulSoup
import re

def get_lottery_data():
    """使用 requests 获取数据"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('https://akjw09d.48489aaa.com:8800/', headers=headers, verify=False)
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
                lottery_div = soup.find(id=code)
                if not lottery_div:
                    continue
                    
                issue_element = lottery_div.find(class_="preDrawIssue")
                if not issue_element:
                    continue
                    
                issue_number = issue_element.text.strip()
                match = re.search(r'(\d+)$', issue_number)
                if not match:
                    continue
                issue_short = match.group(1)[-3:]
                
                number_box = lottery_div.find(class_="number-box")
                if not number_box:
                    continue
                    
                numbers = []
                special_number = None
                special_zodiac = None
                
                number_elements = [li for li in number_box.find_all('li') 
                                 if 'xgcaddF1' not in li.get('class', [])]
                
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
                    
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                
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
                "data": results,
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