from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import re
import os

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--no-zygote')
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    try:
        if os.environ.get('VERCEL_ENV'):
            # Vercel 环境
            chrome_options.binary_location = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
            service = Service(executable_path=os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver'))
        else:
            # GitHub Actions 环境
            service = Service(ChromeDriverManager().install())
            
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        print("Chrome驱动初始化成功")
        return driver
        
    except Exception as e:
        print(f"设置Chrome驱动时出错: {str(e)}")
        if os.environ.get('VERCEL_ENV'):
            print(f"Chrome路径: {os.environ.get('CHROME_BIN')}")
            print(f"ChromeDriver路径: {os.environ.get('CHROMEDRIVER_PATH')}")
        return None

def extract_lottery_info(driver, lottery_code, lottery_name):
    """提取特定彩票的开奖信息"""
    try:
        # 找到对应的彩票区块
        lottery_div = driver.find_element(By.ID, lottery_code)
        if not lottery_div:
            print(f"未找到彩票区块: {lottery_code}")
            return None
        
        # 获取期号
        try:
            issue_element = lottery_div.find_element(By.CLASS_NAME, "preDrawIssue")
            if not issue_element:
                print(f"未找到期号元素")
                return None
                
            issue_number = issue_element.text
            if not issue_number:
                print(f"期号为空")
                return None
                
            issue_number = issue_number.strip()
            print(f"获取到期号: {issue_number}")
            
            match = re.search(r'(\d+)$', issue_number)
            if not match:
                print(f"无法从 {issue_number} 提取期号")
                return None
            issue_short = match.group(1)[-3:]
            print(f"提取的短期号: {issue_short}")
        except Exception as e:
            print(f"处理期号时出错: {str(e)}")
            return None
        
        try:
            number_box = lottery_div.find_element(By.CLASS_NAME, "number-box")
            if not number_box:
                print(f"未找到号码区块")
                return None
                
            number_elements = number_box.find_elements(By.TAG_NAME, "li")
            if not number_elements:
                print(f"未找到号码元素")
                return None
            
            numbers = []
            special_number = None
            special_zodiac = None
            
            valid_elements = [elem for elem in number_elements if "xgcaddF1" not in elem.get_attribute("class")]
            print(f"找到 {len(valid_elements)} 个有效号码元素")
            
            for i, elem in enumerate(valid_elements):
                try:
                    number = elem.find_element(By.TAG_NAME, "span").text
                    if not number:
                        print(f"号码为空")
                        continue
                    number = number.zfill(2)
                    
                    zodiac = elem.find_element(By.CLASS_NAME, "animal").text
                    if not zodiac:
                        print(f"生肖为空")
                        continue
                        
                    print(f"处理第 {i+1} 个号码: {number} {zodiac}")
                    
                    if i == len(valid_elements) - 1:
                        special_number = number
                        special_zodiac = zodiac
                    else:
                        numbers.append(number)
                except Exception as e:
                    print(f"处理单个号码时出错: {str(e)}")
                    continue
            
            if numbers and special_number:
                result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
                print(f"成功生成结果: {result}")
                return result
            else:
                print(f"号码数据不完整: numbers={numbers}, special_number={special_number}")
                return None
                
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
        time.sleep(5)
        
        results = {}
        for lottery_id, (code, name) in lottery_types.items():
            try:
                result = extract_lottery_info(driver, code, name)
                if result:
                    with open(f'{lottery_id}.txt', 'w', encoding='utf-8') as f:
                        f.write(result)
                    results[lottery_id] = result
                    print(f"已保存 {lottery_id} 开奖结果")
                else:
                    print(f"未找到 {name} 的开奖结果")
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                
        return results
                
    except Exception as e:
        print(f"获取开奖结果时出错: {str(e)}")
        return None

def main():
    driver = None
    try:
        driver = get_driver()
        if not driver:
            raise Exception("浏览器初始化失败")
            
        print("浏览器初始化成功")
        results = get_lottery_results(driver)
        
        if os.environ.get('VERCEL_ENV'):
            return results
            
    except Exception as e:
        print(f"运行出错: {str(e)}")
        if os.environ.get('VERCEL_ENV'):
            return {"error": str(e)}
    finally:
        try:
            if driver:
                driver.quit()
                print("浏览器已关闭")
        except Exception as e:
            print(f"关闭浏览器时出错: {str(e)}")

if __name__ == '__main__':
    main()
