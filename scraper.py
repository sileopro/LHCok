from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from datetime import datetime
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
    
    if os.getenv('GITHUB_ACTIONS'):
        chrome_options.binary_location = '/usr/bin/google-chrome'
    
    print("Chrome选项配置完成")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)  # 设置页面加载超时
    print("Chrome驱动初始化成功")
    return driver

def wait_for_element(driver, selector, timeout=20, by=By.CSS_SELECTOR):
    """等待元素出现并返回"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except TimeoutException:
        print(f"等待元素超时: {selector}")
        return None

def get_lottery_result(driver, lottery_type):
    urls = {
        'lam': 'https://www.1292.com/macau',
        'xam': 'https://www.1292.com/newmacau',
        'hk': 'https://www.1292.com/hongkong'
    }
    
    try:
        print(f"\n访问页面: {urls[lottery_type]}")
        driver.get(urls[lottery_type])
        print("页面加载完成")
        
        # 等待页面加载
        time.sleep(15)  # 增加等待时间
        print("开始检查页面元素...")
        
        # 保存页面源码用于分析
        with open(f'debug_{lottery_type}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("已保存页面源码")
        
        # 保存页面截图
        driver.save_screenshot(f'screenshot_{lottery_type}.png')
        print("已保存页面截图")
        
        # 尝试多个可能的选择器
        selectors = {
            'period': [
                '.lottery-period', 
                '.period',
                '[class*="period"]',
                '//div[contains(text(), "期")]',  # XPath
                '//span[contains(text(), "期")]'   # XPath
            ],
            'numbers': [
                '.lottery-number',
                '.number',
                '[class*="number"]',
                '//div[contains(@class, "number")]',  # XPath
                '//span[contains(@class, "number")]'  # XPath
            ]
        }
        
        # 获取期数
        period = None
        for selector in selectors['period']:
            try:
                if selector.startswith('//'):
                    element = wait_for_element(driver, selector, by=By.XPATH)
                else:
                    element = wait_for_element(driver, selector)
                if element:
                    period = element.text
                    print(f"找到期数: {period}")
                    break
            except Exception as e:
                print(f"尝试选择器 {selector} 失败: {str(e)}")
        
        # 获取号码
        numbers_text = ""
        for selector in selectors['numbers']:
            try:
                if selector.startswith('//'):
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    numbers_text = ' '.join([num.text for num in elements if num.text.strip()])
                    print(f"找到号码: {numbers_text}")
                    break
            except Exception as e:
                print(f"尝试选择器 {selector} 失败: {str(e)}")
        
        if period or numbers_text:
            result = (
                f"期数: {period if period else '未知'}\n"
                f"开奖时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"号码: {numbers_text if numbers_text else '未知'}\n"
            )
            
            with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f'{lottery_type} 更新成功：\n{result}')
        else:
            print(f"未能找到 {lottery_type} 的开奖信息")
            
    except Exception as e:
        print(f'获取 {lottery_type} 结果失败: {str(e)}')
        if 'driver' in locals():
            driver.save_screenshot(f'error_{lottery_type}.png')
            with open(f'error_{lottery_type}.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)

def main():
    lottery_types = ['lam', 'xam', 'hk']
    
    try:
        print("开始初始化Chrome浏览器...")
        driver = setup_driver()
        print("浏览器初始化成功")
        
        for lottery_type in lottery_types:
            print(f'\n正在获取 {lottery_type} 的开奖结果...')
            get_lottery_result(driver, lottery_type)
            time.sleep(5)
            
    except Exception as e:
        print(f"运行出错: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("浏览器已关闭")

if __name__ == '__main__':
    main()
