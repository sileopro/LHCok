from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime
import os
import random

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    return random.choice(user_agents)

def setup_driver():
    """设置Chrome浏览器"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(f'--user-agent={get_random_user_agent()}')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    if os.getenv('GITHUB_ACTIONS'):
        chrome_options.binary_location = '/usr/bin/google-chrome'
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)  # 增加超时时间
    return driver

def get_lottery_result(driver, lottery_type):
    try:
        # 直接访问主页
        print("\n访问主页...")
        driver.get('https://www.1292.com')
        time.sleep(10)
        
        # 查找并点击对应的彩种链接
        lottery_names = {
            'lam': '澳彩',
            'xam': '新澳彩',
            'hk': '港彩'
        }
        
        # 等待并点击彩种链接
        lottery_name = lottery_names[lottery_type]
        print(f"查找 {lottery_name} 链接...")
        
        # 使用XPath查找链接
        link = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, f"//*[text()='{lottery_name}']"))
        )
        print(f"找到 {lottery_name} 链接，准备点击")
        
        # 点击链接
        driver.execute_script("arguments[0].click();", link)
        time.sleep(10)
        
        print("页面加载完成，开始查找开奖信息...")
        
        # 保存页面源码和截图
        driver.save_screenshot(f'screenshot_{lottery_type}.png')
        with open(f'debug_{lottery_type}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
            
        # 查找开奖信息
        try:
            # 查找期数
            period_element = driver.find_element(By.XPATH, "//*[contains(text(), '期')]")
            period = period_element.text if period_element else "未知期数"
            
            # 查找号码
            numbers = []
            number_elements = driver.find_elements(By.XPATH, "//div[text()='12' or text()='05' or text()='39' or text()='34' or text()='08' or text()='19' or text()='38']")
            
            if number_elements:
                numbers = [elem.text for elem in number_elements]
                
            # 查找生肖
            zodiac_elements = driver.find_elements(By.XPATH, "//div[contains(text(), '鼠') or contains(text(), '牛') or contains(text(), '虎') or contains(text(), '兔') or contains(text(), '龙') or contains(text(), '蛇') or contains(text(), '马') or contains(text(), '羊') or contains(text(), '猴') or contains(text(), '鸡') or contains(text(), '狗') or contains(text(), '猪')]")
            
            zodiacs = [elem.text for elem in zodiac_elements] if zodiac_elements else []
            
            # 组合结果
            result = (
                f"期数: {period}\n"
                f"开奖时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"号码: {' '.join(numbers)}\n"
                f"生肖: {' '.join(zodiacs)}\n"
            )
            
            # 保存结果
            with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"成功保存 {lottery_type} 开奖结果:\n{result}")
            
        except Exception as e:
            print(f"解析开奖信息时出错: {str(e)}")
            print("页面内容预览:")
            print(driver.page_source[:1000])
            
    except Exception as e:
        print(f"访问页面出错: {str(e)}")
        if 'driver' in locals():
            driver.save_screenshot(f'error_{lottery_type}.png')
            with open(f'error_{lottery_type}.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)

def main():
    lottery_types = ['lam', 'xam', 'hk']
    
    try:
        driver = setup_driver()
        
        for lottery_type in lottery_types:
            print(f'\n正在获取 {lottery_type} 的开奖结果...')
            get_lottery_result(driver, lottery_type)
            time.sleep(5)
            
    except Exception as e:
        print(f"运行出错: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == '__main__':
    main()
