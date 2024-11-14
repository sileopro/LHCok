from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import requests
import time
import re
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'sec-ch-ua': '"Google Chrome";v="119"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        session = requests.Session()
        
        # 首先访问一次获取cookies
        print("第一次访问获取cookies...")
        response = session.get(url, headers=headers, verify=False, timeout=30)
        print(f"初始请求状态码: {response.status_code}")
        
        # 等待一下模拟真实浏览器行为
        time.sleep(2)
        
        # 再次访问
        print("第二次访问获取实际内容...")
        response = session.get(url, headers=headers, verify=False, timeout=30)
        print(f"第二次请求状态码: {response.status_code}")
        
        if not response.text:
            print("服务器返回空响应")
            return {"error": "Empty response from server"}
            
        print(f"响应内容长度: {len(response.text)}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查页面内容
        print("页面标题:", soup.title.string if soup.title else "无标题")
        print("页面内容预览:", response.text[:200])
        
        # 检查是否有反爬虫JavaScript
        if 'display:none' in response.text:
            print("检测到反爬虫JavaScript，尝试绕过...")
            # 直接从响应文本中提取数据
            content = response.text
            results = {}
            
            lottery_types = {
                'lam': ('AMLHC2', '老澳门六合彩'),
                'xam': ('AMLHC3', '新澳门六合彩'),
                'hk': ('LHC', '六合彩'),
                'tc': ('TWLHC', '台湾六合彩')
            }
            
            for lottery_id, (code, name) in lottery_types.items():
                try:
                    # 使用正则表达式直接从HTML中提取数据
                    pattern = f'id="{code}".*?class="preDrawIssue">(.*?)</div>.*?class="number-box">(.*?)</div>'
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        issue = match.group(1).strip()
                        numbers_html = match.group(2)
                        
                        # 提取号码
                        number_pattern = r'<span.*?>(.*?)</span>'
                        numbers = re.findall(number_pattern, numbers_html)
                        
                        if numbers:
                            result = f"第{issue[-3:]}期：{' '.join(num.zfill(2) for num in numbers[:-1])} 特码 {numbers[-1].zfill(2)}"
                            results[lottery_id] = result
                            print(f"成功提取 {name}: {result}")
                except Exception as e:
                    print(f"处理 {name} 时出错: {str(e)}")
                    continue
            
            if results:
                return results
                
        # 如果没有找到结果，返回错误
        print("未找到任何彩票结果")
        return {"error": "No lottery results found"}
        
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
