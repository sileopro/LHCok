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
    chrome_options.add_argument('--window-size=1920,1080')
    
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

def extract_lottery_info(driver, lottery_type):
    """提取特定彩票的开奖信息"""
    try:
        # 等待并点击图库按钮
        gallery_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '图库')]"))
        )
        driver.execute_script("arguments[0].click();", gallery_button)
        time.sleep(2)

        # 点击对应的彩种按钮
        lottery_buttons = {
            'lam': '澳彩',
            'xam': '新澳彩',
            'hk': '港彩',
            'tc': '台彩'
        }
        
        # 等待并点击彩种按钮
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[text()='{lottery_buttons[lottery_type]}']"))
        )
        driver.execute_script("arguments[0].click();", button)
        time.sleep(2)

        # 获取期号
        issue_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '第') and contains(text(), '期')]"))
        )
        issue_text = issue_element.text.strip()
        match = re.search(r'第(\d+)期', issue_text)
        if not match:
            raise Exception(f"无法从文本'{issue_text}'解析期号")
        issue_short = match.group(1)[-3:]

        # 获取号码
        numbers = []
        number_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'circle') or contains(@class, 'number')]//span"))
        )
        
        for i, elem in enumerate(number_elements[:-1]):  # 除了最后一个数字
            number = elem.text.strip().zfill(2)
            numbers.append(number)
        
        # 获取特码和生肖
        special_number = number_elements[-1].text.strip().zfill(2)
        
        # 获取生肖
        zodiac_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'zodiac') or contains(@class, 'animal')]"))
        )
        special_zodiac = zodiac_element.text.strip()

        result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
        print(f"成功获取{lottery_buttons[lottery_type]}开奖结果：{result}")
        return result

    except Exception as e:
        print(f"提取{lottery_type}信息时出错: {str(e)}")
        return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    try:
        driver.get('https://6htv99.com/#/home')
        time.sleep(5)  # 等待页面加载
        
        results = {}
        lottery_types = ['lam', 'xam', 'hk', 'tc']
        
        for lottery_type in lottery_types:
            try:
                result = extract_lottery_info(driver, lottery_type)
                if result:
                    with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                        f.write(result)
                    results[lottery_type] = result
                    print(f"已保存 {lottery_type} 开奖结果")
                else:
                    print(f"未找到 {lottery_type} 的开奖结果")
                # 每次处理完一个彩种后，重新加载页面
                driver.get('https://6htv99.com/#/home')
                time.sleep(3)
            except Exception as e:
                print(f"处理 {lottery_type} 时出错: {str(e)}")
                driver.get('https://6htv99.com/#/home')
                time.sleep(3)
                
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
