from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import requests
try:
    from bs4 import BeautifulSoup
except ImportError:
    import pip
    pip.main(['install', 'beautifulsoup4'])
    from bs4 import BeautifulSoup
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_lottery():
    """使用 requests 和 BeautifulSoup 替代 Selenium"""
    try:
        url = 'https://akjw09d.48489aaa.com:8800/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()  # 检查响应状态
        
        if not response.text:
            return {"error": "Empty response from server"}
            
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
                    issue = div.find('div', class_='preDrawIssue')
                    if not issue:
                        continue
                    issue_text = issue.text.strip()
                    
                    numbers = div.find_all('li', class_='ball')
                    if not numbers:
                        continue
                        
                    result = f"第{issue_text[-3:]}期：" + " ".join([num.text.strip().zfill(2) for num in numbers[:-1]])
                    result += f" 特码 {numbers[-1].text.strip().zfill(2)}"
                    results[lottery_id] = result
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                continue
                
        return results if results else {"error": "No lottery results found"}
        
    except requests.RequestException as e:
        print(f"请求错误: {str(e)}")
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        print(f"爬取过程出错: {str(e)}")
        return {"error": str(e)}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print("开始执行爬虫...")
            results = scrape_lottery()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_data = {
                "status": "success" if "error" not in results else "error",
                "data": results if "error" not in results else None,
                "error": results.get("error"),
                "message": "Scraper executed successfully" if "error" not in results else "Scraper execution failed"
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
