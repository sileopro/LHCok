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
    """使用 requests 获取数据"""
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
        
        results = {}
        
        # 查找所有包含开奖结果的区块
        lottery_blocks = soup.find_all('div', class_=lambda x: x and '六合彩' in x.get_text())
        
        for block in lottery_blocks:
            try:
                # 获取彩票名称
                title = block.find_previous('div', text=re.compile('.*六合彩.*')).text.strip()
                
                # 确定彩票类型
                lottery_id = None
                if '新澳门' in title:
                    lottery_id = 'xam'
                elif '老澳门' in title:
                    lottery_id = 'lam'
                elif '台湾' in title:
                    lottery_id = 'tc'
                elif '六合彩' in title:
                    lottery_id = 'hk'
                
                if not lottery_id:
                    continue
                
                # 获取期号
                issue_text = block.find(string=re.compile('第.*期'))
                if not issue_text:
                    continue
                    
                issue_match = re.search(r'第(\d+)期', issue_text)
                if not issue_match:
                    continue
                    
                issue_short = issue_match.group(1)[-3:]
                
                # 获取号码
                numbers = []
                special_number = None
                special_zodiac = None
                
                number_elements = block.find_all(['span', 'div'], class_=lambda x: x and ('number' in x or '号码' in x))
                
                for i, elem in enumerate(number_elements):
                    number = elem.text.strip().zfill(2)
                    zodiac = elem.find_next(string=re.compile('[鼠牛虎兔龙蛇马羊猴鸡狗猪]'))
                    
                    if i == len(number_elements) - 1:
                        special_number = number
                        special_zodiac = zodiac.strip() if zodiac else ''
                    else:
                        numbers.append(number)
                
                if numbers and special_number:
                    results[lottery_id] = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
                    print(f"成功获取 {title} 结果")
                
            except Exception as e:
                print(f"处理彩票区块时出错: {str(e)}")
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