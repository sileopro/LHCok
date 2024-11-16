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
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'图库')]"))
        )
        gallery_button.click()
        time.sleep(2)

        # 根据彩票类型点击对应按钮
        lottery_buttons = {
            'lam': '澳彩',
            'xam': '新澳彩',
            'hk': '港彩',
            'tc': '台彩'
        }
        
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(),'{lottery_buttons[lottery_type]}')]"))
        )
        button.click()
        time.sleep(2)

        # 获取最新一期开奖信息
        issue_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "period"))
        )
        issue_number = issue_element.text.strip()
        match = re.search(r'第(\d+)期', issue_number)
        if match:
            issue_short = match.group(1)[-3:]
        else:
            raise Exception("无法解析期号")

        # 获取开奖号码
        number_elements = driver.find_elements(By.CLASS_NAME, "number-item")
        numbers = []
        for elem in number_elements[:-1]:  # 除最后一个数字外的所有数字
            number = elem.text.strip().zfill(2)
            numbers.append(number)
        
        # 获取特码和生肖
        special_elem = number_elements[-1]
        special_number = special_elem.text.strip().zfill(2)
        zodiac = driver.find_element(By.CLASS_NAME, "zodiac").text.strip()

        result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {zodiac}"
        return result

    except Exception as e:
        print(f"提取{lottery_type}信息时出错: {str(e)}")
        return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    try:
        driver.get('https://6htv99.com/#/home')
        time.sleep(5)
        
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
            except Exception as e:
                print(f"处理 {lottery_type} 时出错: {str(e)}")
                
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
