from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re
import os

def setup_driver():
    """设置Chrome浏览器"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_lottery_info(driver, lottery_code, lottery_name):
    """提取特定彩票的开奖信息"""
    try:
        # 找到对应的彩票区块
        lottery_div = driver.find_element(By.ID, lottery_code)
        
        # 获取期号
        issue_element = lottery_div.find_element(By.CLASS_NAME, "preDrawIssue")
        issue_number = issue_element.text.strip()
        # 提取期号中的最后三位数字
        match = re.search(r'(\d+)$', issue_number)
        if match:
            issue_short = match.group(1)[-3:]
        else:
            print(f"无法从 {issue_number} 提取期号")
            return None
        
        # 获取开奖号码
        numbers = []
        special_number = None
        special_zodiac = None
        number_box = lottery_div.find_element(By.CLASS_NAME, "number-box")
        number_elements = number_box.find_elements(By.TAG_NAME, "li")
        
        valid_elements = [elem for elem in number_elements if "xgcaddF1" not in elem.get_attribute("class")]
        
        for i, elem in enumerate(valid_elements):
            try:
                number = elem.find_element(By.TAG_NAME, "span").text.zfill(2)  # 确保数字是两位
                zodiac = elem.find_element(By.CLASS_NAME, "animal").text
                if i == len(valid_elements) - 1:  # 最后一个数字是特码
                    special_number = number
                    special_zodiac = zodiac
                else:
                    numbers.append(number)
            except Exception as e:
                print(f"处理号码元素时出错: {str(e)}")
                continue
        
        if numbers and special_number:
            # 格式化输出
            result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
            return result
            
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
        # 访问页面
        driver.get('https://akjw09d.48489aaa.com:8800/')
        time.sleep(5)
        
        # 对每种彩票类型进行处理
        for lottery_id, (code, name) in lottery_types.items():
            try:
                result = extract_lottery_info(driver, code, name)
                if result:
                    # 使用绝对路径保存文件
                    file_path = os.path.join(os.getcwd(), f'{lottery_id}.txt')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"已保存 {lottery_id} 开奖结果到 {file_path}")
                else:
                    print(f"未找到 {name} 的开奖结果")
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                
    except Exception as e:
        print(f"获取开奖结果时出错: {str(e)}")

def main():
    while True:  # 添加循环以支持持续运行
        try:
            driver = setup_driver()
            print("浏览器初始化成功")
            
            get_lottery_results(driver)
            
        except Exception as e:
            print(f"运行出错: {str(e)}")
        finally:
            if 'driver' in locals():
                driver.quit()
                print("浏览器已关闭")
        
        # 检查是否是通过 Vercel 运行
        if os.environ.get('VERCEL_ENV'):
            break  # Vercel 环境下只运行一次
        
        print("等待下一次运行...")
        time.sleep(300)  # 每5分钟运行一次

if __name__ == '__main__':
    main()
