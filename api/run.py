from http.server import BaseHTTPRequestHandler
import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import main

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print("开始执行爬虫...")
            results = main()  # 运行爬虫
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # 确保返回的是有效的 JSON
            response_data = {
                "status": "success",
                "data": results if results else {},
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
