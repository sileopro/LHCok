from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime

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
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_lottery_info(driver, lottery_name):
    """提取指定彩种的开奖信息"""
    try:
        # 查找包含彩种名称的区域
        sections = driver.find_elements(By.XPATH, f"//div[contains(text(), '{lottery_name}')]/../..")
        for section in sections:
            # 获取期数
            period_elem = section.find_element(By.XPATH, ".//div[contains(text(), '第') and contains(text(), '期')]")
            if period_elem:
                period = period_elem.text.split('第')[1].split('开奖')[0].strip()
                
                # 获取号码和生肖
                result_elements = section.find_elements(By.XPATH, ".//div[contains(@class, 'history')]/following-sibling::div//text()")
                numbers = []
                zodiacs = []
                
                for i in range(0, len(result_elements), 2):
                    if i+1 < len(result_elements):
                        num = result_elements[i].text.strip()
                        zodiac = result_elements[i+1].text.strip()
                        if num.isdigit():
                            numbers.append(num)
                            zodiacs.append(zodiac)
                
                if numbers and zodiacs:
                    result = (
                        f"{lottery_name}\n"
                        f"第 {period} 开奖结果\n"
                        f"{' '.join([f'{num}{zodiac}' for num, zodiac in zip(numbers, zodiacs)])}\n"
                    )
                    return result
    except Exception as e:
        print(f"提取 {lottery_name} 信息时出错: {str(e)}")
    return None

def get_lottery_results(driver):
    """获取所有彩种开奖结果"""
    lottery_mapping = {
        'lam': '老澳门六合彩',
        'xam': '新澳门六合彩',
        'hk': '六合彩',
        'tc': '台湾六合彩'
    }
    
    try:
        # 访问页面
        driver.get('https://akjw09d.48489aaa.com:8800/')
        time.sleep(5)
        
        # 执行JavaScript来显示内容
        driver.execute_script("document.body.style.display = 'block';")
        time.sleep(3)
        
        # 获取各彩种结果
        for code, name in lottery_mapping.items():
            result = extract_lottery_info(driver, name)
            if result:
                with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"已保存 {name} 开奖结果")
            else:
                print(f"未找到 {name} 开奖结果")
                
    except Exception as e:
        print(f"获取开奖结果时出错: {str(e)}")

def main():
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

if __name__ == '__main__':
    main()
