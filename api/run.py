from http.server import BaseHTTPRequestHandler
import sys
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import re

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    try:
        if os.environ.get('VERCEL_ENV'):
            chrome_options.binary_location = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
            service = Service(executable_path=os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver'))
        else:
            service = Service()
            
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        return driver
    except Exception as e:
        print(f"设置Chrome驱动时出错: {str(e)}")
        return None

def extract_lottery_info(driver, lottery_code, lottery_name):
    """提取特定彩票的开奖信息"""
    try:
        lottery_div = driver.find_element(By.ID, lottery_code)
        if not lottery_div:
            print(f"未找到彩票区块: {lottery_code}")
            return None
        
        try:
            issue_element = lottery_div.find_element(By.CLASS_NAME, "preDrawIssue")
            if not issue_element:
                return None
                
            issue_number = issue_element.text.strip()
            match = re.search(r'(\d+)$', issue_number)
            if not match:
                return None
            issue_short = match.group(1)[-3:]
            
        except Exception as e:
            print(f"处理期号时出错: {str(e)}")
            return None
        
        try:
            number_box = lottery_div.find_element(By.CLASS_NAME, "number-box")
            number_elements = number_box.find_elements(By.TAG_NAME, "li")
            
            numbers = []
            special_number = None
            special_zodiac = None
            
            valid_elements = [elem for elem in number_elements if "xgcaddF1" not in elem.get_attribute("class")]
            
            for i, elem in enumerate(valid_elements):
                try:
                    number = elem.find_element(By.TAG_NAME, "span").text.strip().zfill(2)
                    zodiac = elem.find_element(By.CLASS_NAME, "animal").text.strip()
                    
                    if i == len(valid_elements) - 1:
                        special_number = number
                        special_zodiac = zodiac
                    else:
                        numbers.append(number)
                except Exception as e:
                    continue
            
            if numbers and special_number:
                result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
                return result
                
        except Exception as e:
            print(f"处理号码区块时出错: {str(e)}")
            return None
            
    except Exception as e:
        print(f"提取{lottery_name}信息时出错: {str(e)}")
        return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    lottery_types = {
        'lam': ('AMLHC2', '老澳门六合彩'),
        'xam': ('AMLHC3', '新澳门六合彩'),
        'hk': ('LHC', '六合彩'),
        'tc': ('TWLHC', '台湾六合彩')
    }
    
    try:
        driver.get('https://akjw09d.48489aaa.com:8800/')
        time.sleep(5)  # 等待页面加载
        
        results = {}
        for lottery_id, (code, name) in lottery_types.items():
            try:
                result = extract_lottery_info(driver, code, name)
                if result:
                    results[lottery_id] = result
                    print(f"已获取 {lottery_id} 开奖结果")
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                
        return results
                
    except Exception as e:
        print(f"获取开奖结果时出错: {str(e)}")
        return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print("开始执行爬虫...")
            driver = get_driver()
            if not driver:
                raise Exception("浏览器初始化失败")
                
            print("浏览器初始化成功")
            results = get_lottery_results(driver)
            
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