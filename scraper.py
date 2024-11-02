from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
    
    # 在GitHub Actions环境中
    if os.getenv('GITHUB_ACTIONS'):
        chrome_options.binary_location = '/usr/bin/google-chrome'
    
    print("Chrome选项配置完成")
    driver = webdriver.Chrome(options=chrome_options)
    print("Chrome驱动初始化成功")
    return driver

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
        
        wait = WebDriverWait(driver, 20)
        print("等待页面元素加载...")
        
        # 等待加载动画消失
        time.sleep(10)  # 增加等待时间
        print("页面准备就绪")
        
        # 保存页面截图用于调试
        driver.save_screenshot(f'screenshot_{lottery_type}.png')
        print(f"页面截图已保存为 screenshot_{lottery_type}.png")
        
        # 获取开奖信息
        print("开始获取开奖信息...")
        if lottery_type == 'lam':
            period = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.lottery-period'))).text
            numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.lottery-number')))
            numbers_text = ' '.join([num.text for num in numbers])
            
        elif lottery_type == 'xam':
            period = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.lottery-period'))).text
            numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.lottery-number')))
            numbers_text = ' '.join([num.text for num in numbers])
            
        elif lottery_type == 'hk':
            period = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.lottery-period'))).text
            numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.lottery-number')))
            numbers_text = ' '.join([num.text for num in numbers])
        
        result = (
            f"期数: {period}\n"
            f"开奖时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"号码: {numbers_text}\n"
        )
        
        with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
            f.write(result)
        print(f'{lottery_type} 更新成功：\n{result}')
        
        # 保存页面源码
        with open(f'debug_{lottery_type}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
            
    except Exception as e:
        print(f'获取 {lottery_type} 结果失败: {str(e)}')
        # 保存错误页面源码和截图
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
            time.sleep(3)
            
    except Exception as e:
        print(f"运行出错: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("浏览器已关闭")

if __name__ == '__main__':
    main()
