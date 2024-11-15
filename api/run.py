from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import subprocess
import time

def get_lottery_data():
    """使用 Node.js 的 Puppeteer 获取数据"""
    try:
        # 执行 Node.js 脚本
        process = subprocess.Popen(['node', 'api/scraper.js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if stderr:
            print(f"Node.js 错误输出: {stderr.decode('utf-8')}")
            
        if stdout:
            try:
                return json.loads(stdout.decode('utf-8'))
            except json.JSONDecodeError:
                print(f"JSON解析错误: {stdout.decode('utf-8')}")
                return None
        
        return None
        
    except Exception as e:
        print(f"执行脚本时出错: {str(e)}")
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