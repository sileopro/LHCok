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
    
    # 添加更多的浏览器参数
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    if os.getenv('GITHUB_ACTIONS'):
        chrome_options.binary_location = '/usr/bin/google-chrome'
    
    print("Chrome选项配置完成")
    driver = webdriver.Chrome(options=chrome_options)
    
    # 修改 navigator.webdriver 标志
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    driver.set_page_load_timeout(30)
    print("Chrome驱动初始化成功")
    return driver

def bypass_cloudflare(driver, url):
    """尝试绕过 Cloudflare 检测"""
    try:
        driver.get(url)
        time.sleep(5)  # 等待初始加载
        
        # 检查是否存在 Cloudflare 挑战页面
        if "Just a moment" in driver.page_source or "Checking your browser" in driver.page_source:
            print("检测到 Cloudflare 验证，等待...")
            time.sleep(10)  # 等待 Cloudflare 验证通过
            
        return True
    except Exception as e:
        print(f"绕过 Cloudflare 失败: {str(e)}")
        return False

def get_lottery_result(driver, lottery_type):
    base_url = 'https://www.1292.com'
    urls = {
        'lam': f'{base_url}/macau',
        'xam': f'{base_url}/newmacau',
        'hk': f'{base_url}/hongkong'
    }
    
    try:
        print(f"\n访问页面: {urls[lottery_type]}")
        
        # 先访问主页
        if not bypass_cloudflare(driver, base_url):
            print("无法访问主页")
            return
            
        time.sleep(3)
        
        # 再访问具体页面
        if not bypass_cloudflare(driver, urls[lottery_type]):
            print("无法访问彩票页面")
            return
            
        print("页面加载完成")
        
        # 等待页面加载
        time.sleep(10)
        print("开始检查页面元素...")
        
        # 打印页面标题和URL
        print(f"当前页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        
        # 保存页面源码
        page_source = driver.page_source
        with open(f'debug_{lottery_type}.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("已保存页面源码")
        
        # 保存页面截图
        driver.save_screenshot(f'screenshot_{lottery_type}.png')
        print("已保存页面截图")
        
        # 打印页面文本内容的一部分
        print("页面文本预览:")
        print(driver.find_element(By.TAG_NAME, 'body').text[:500])
        
        # 尝试查找开奖信息
        try:
            # 等待页面加载完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 执行JavaScript来获取页面内容
            page_text = driver.execute_script("return document.body.innerText")
            
            # 查找包含"期"的文本
            if "期" in page_text:
                print("找到期数相关文本")
                # 获取包含"期"的元素
                elements = driver.find_elements(By.XPATH, "//*[contains(text(), '期')]")
                for element in elements:
                    print(f"找到文本: {element.text}")
                    
            # 查找数字
            number_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'num')] | //span[contains(@class, 'num')]")
            if number_elements:
                numbers_text = ' '.join([e.text for e in number_elements if e.text.strip()])
                print(f"找到号码: {numbers_text}")
                
        except Exception as e:
            print(f"查找元素时出错: {str(e)}")
            
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
