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
    chrome_options.add_argument('--headless')  # 无界面模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    return webdriver.Chrome(options=chrome_options)

def get_lottery_result(driver, lottery_type):
    # 页面URL映射
    urls = {
        'lam': 'https://www.1292.com/macau',  # 澳彩
        'xam': 'https://www.1292.com/newmacau',  # 新澳彩
        'hk': 'https://www.1292.com/hongkong'  # 港彩
    }
    
    try:
        print(f"\n访问页面: {urls[lottery_type]}")
        driver.get(urls[lottery_type])
        
        # 等待页面加载完成（等待开奖结果出现）
        wait = WebDriverWait(driver, 20)
        
        # 等待加载动画消失
        time.sleep(5)  # 给予足够时间加载
        
        # 获取开奖信息
        if lottery_type == 'lam':
            # 澳彩
            period = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.lottery-period'))).text
            numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.lottery-number')))
            numbers_text = ' '.join([num.text for num in numbers])
            
        elif lottery_type == 'xam':
            # 新澳彩
            period = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.lottery-period'))).text
            numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.lottery-number')))
            numbers_text = ' '.join([num.text for num in numbers])
            
        elif lottery_type == 'hk':
            # 港彩
            period = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.lottery-period'))).text
            numbers = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.lottery-number')))
            numbers_text = ' '.join([num.text for num in numbers])
        
        # 保存结果
        result = (
            f"期数: {period}\n"
            f"开奖时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"号码: {numbers_text}\n"
        )
        
        with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
            f.write(result)
        print(f'{lottery_type} 更新成功：\n{result}')
        
        # 保存页面源码用于调试
        with open(f'debug_{lottery_type}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
            
    except Exception as e:
        print(f'获取 {lottery_type} 结果失败: {str(e)}')
        # 保存错误页面源码
        with open(f'error_{lottery_type}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)

def main():
    lottery_types = ['lam', 'xam', 'hk']
    
    try:
        driver = setup_driver()
        print("浏览器初始化成功")
        
        for lottery_type in lottery_types:
            print(f'\n正在获取 {lottery_type} 的开奖结果...')
            get_lottery_result(driver, lottery_type)
            time.sleep(3)  # 请求间隔
            
    except Exception as e:
        print(f"运行出错: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == '__main__':
    main()
