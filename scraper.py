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
    
    # 禁用JavaScript检测
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # 修改 navigator.webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def get_lottery_result(driver, lottery_type):
    try:
        print(f"\n正在获取 {lottery_type} 的开奖结果...")
        
        # 访问页面
        driver.get('https://akjw09d.48489aaa.com:8800/')
        
        # 等待页面加载
        time.sleep(5)
        
        # 执行JavaScript来显示内容
        driver.execute_script("document.body.style.display = 'block';")
        
        # 再等待一下确保内容加载
        time.sleep(3)
        
        # 保存页面源码和截图用于调试
        driver.save_screenshot(f'screenshot_{lottery_type}.png')
        with open(f'debug_{lottery_type}.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        # 打印页面标题和URL
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        
        # 打印页面文本内容
        print("页面内容:")
        print(driver.find_element(By.TAG_NAME, 'body').text)
        
        # 查找开奖信息
        try:
            # 等待内容加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 获取所有文本内容
            page_text = driver.execute_script("return document.body.innerText")
            print("\n页面文本内容:")
            print(page_text)
            
            # 查找包含期数的文本
            elements = driver.find_elements(By.XPATH, "//*[contains(text(), '期')]")
            if elements:
                print("\n找到期数元素:")
                for elem in elements:
                    print(elem.text)
            
            # 查找数字
            number_elements = driver.find_elements(By.XPATH, "//div[contains(text(), '12') or contains(text(), '05') or contains(text(), '39')]")
            if number_elements:
                print("\n找到数字元素:")
                for elem in number_elements:
                    print(elem.text)
                    
        except Exception as e:
            print(f"解析元素时出错: {str(e)}")
            
    except Exception as e:
        print(f"访问页面出错: {str(e)}")

def main():
    lottery_types = ['lam', 'xam', 'hk']
    
    try:
        driver = setup_driver()
        print("浏览器初始化成功")
        
        for lottery_type in lottery_types:
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
