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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        print(f"开始请求 URL: {url}")
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        print(f"请求状态码: {response.status_code}")
        response.raise_for_status()
        
        if not response.text:
            print("服务器返回空响应")
            return {"error": "Empty response from server"}
            
        print(f"响应内容长度: {len(response.text)}")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查页面内容
        print("页面标题:", soup.title.string if soup.title else "无标题")
        
        results = {}
        lottery_types = {
            'lam': ('AMLHC2', '老澳门六合彩'),
            'xam': ('AMLHC3', '新澳门六合彩'),
            'hk': ('LHC', '六合彩'),
            'tc': ('TWLHC', '台湾六合彩')
        }
        
        for lottery_id, (code, name) in lottery_types.items():
            try:
                print(f"\n处理 {name} ({code})")
                div = soup.find('div', id=code)
                if not div:
                    print(f"未找到 {code} 的div元素")
                    continue
                    
                print(f"找到 {code} 的div元素")
                issue = div.find('div', class_='preDrawIssue')
                if not issue:
                    print(f"未找到期号元素")
                    continue
                    
                issue_text = issue.text.strip()
                print(f"期号: {issue_text}")
                
                numbers = div.find_all('li', class_='ball')
                if not numbers:
                    print(f"未找到号码元素")
                    continue
                    
                print(f"找到 {len(numbers)} 个号码")
                result = f"第{issue_text[-3:]}期：" + " ".join([num.text.strip().zfill(2) for num in numbers[:-1]])
                result += f" 特码 {numbers[-1].text.strip().zfill(2)}"
                results[lottery_id] = result
                print(f"结果: {result}")
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                continue
                
        if not results:
            print("未找到任何彩票结果")
            # 打印页面结构以便调试
            print("\n页面结构:")
            print(soup.prettify()[:1000])  # 只打印前1000个字符
            return {"error": "No lottery results found"}
            
        return results
        
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
