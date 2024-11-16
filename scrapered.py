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
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        return driver
    except Exception as e:
        print(f"设置Chrome驱动时出错: {str(e)}")
        return None

def extract_lottery_info(driver):
    """提取开奖信息"""
    try:
        # 等待期号元素加载
        issue_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'period') or contains(text(), '第')]"))
        )
        issue_text = issue_element.text.strip()
        match = re.search(r'第(\d+)期', issue_text)
        if match:
            issue_short = match.group(1)[-3:]
        else:
            raise Exception("无法解析期号")

        # 获取所有号码
        number_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'number')]//span[text()]"))
        )
        
        numbers = []
        for i, elem in enumerate(number_elements):
            number = elem.text.strip().zfill(2)
            if i < len(number_elements) - 1:
                numbers.append(number)
            else:
                special_number = number

        # 获取生肖
        zodiac_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'zodiac') or contains(@class, 'animal')]")
        if zodiac_elements:
            special_zodiac = zodiac_elements[-1].text.strip()
        else:
            special_zodiac = ""

        result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
        return result

    except Exception as e:
        print(f"提取开奖信息时出错: {str(e)}")
        return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    try:
        driver.get('https://6htv99.com/#/home')
        time.sleep(5)  # 等待页面加载
        
        # 获取主页面的开奖信息
        result = extract_lottery_info(driver)
        if result:
            # 保存到所有文件中，因为主页显示的是最新的开奖结果
            lottery_types = ['lam', 'xam', 'hk', 'tc']
            for lottery_type in lottery_types:
                with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"已保存 {lottery_type} 开奖结果")
            return {"result": result}
        else:
            print("未找到开奖结果")
            return None
                
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
