from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import requests
from bs4 import BeautifulSoup

def scrape_lottery():
    """使用 requests 和 BeautifulSoup 替代 Selenium"""
    try:
        url = 'https://akjw09d.48489aaa.com:8800/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = {}
        lottery_types = {
            'lam': ('AMLHC2', '老澳门六合彩'),
            'xam': ('AMLHC3', '新澳门六合彩'),
            'hk': ('LHC', '六合彩'),
            'tc': ('TWLHC', '台湾六合彩')
        }
        
        for lottery_id, (code, name) in lottery_types.items():
            try:
                div = soup.find('div', id=code)
                if div:
                    issue = div.find('div', class_='preDrawIssue').text.strip()
                    numbers = div.find_all('li', class_='ball')
                    result = f"第{issue[-3:]}期：" + " ".join([num.text.strip().zfill(2) for num in numbers[:-1]])
                    result += f" 特码 {numbers[-1].text.strip().zfill(2)}"
                    results[lottery_id] = result
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                
        return results
    except Exception as e:
        print(f"爬取过程出错: {str(e)}")
        return {"error": str(e)}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print("开始执行爬虫...")
            results = scrape_lottery()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if isinstance(results, dict) and 'error' in results:
                error_response = {
                    "status": "error",
                    "error": results['error'],
                    "message": "Scraper execution failed"
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
            response_data = {
                "status": "success",
                "data": results,
                "message": "Scraper executed successfully"
            }
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            print(f"执行出错: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            error_response = {
                "status": "error",
                "error": str(e),
                "message": "Scraper execution failed"
            }
            
            self.wfile.write(json.dumps(error_response).encode('utf-8')) 
