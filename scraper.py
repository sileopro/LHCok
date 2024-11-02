from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re

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
    return driver

def extract_lottery_info(driver, lottery_name):
    """提取特定彩票的开奖信息"""
    try:
        # 找到包含彩票名称的区域
        section = driver.find_element(By.XPATH, f"//div[contains(text(), '{lottery_name}')]/ancestor::div[contains(., '开奖结果')][1]")
        
        # 获取期号
        issue_text = section.find_element(By.XPATH, ".//div[starts-with(text(), '第')]").text
        issue_number = re.search(r'第\s*(\d+)', issue_text).group(1)
        
        # 获取所有数字和生肖对
        numbers_text = section.find_element(By.XPATH, ".//div[contains(@class, 'lottery-numbers') or contains(@style, 'display: flex')]").text
        number_pairs = re.findall(r'(\d+)\s*([猪鼠牛虎兔龙蛇马羊猴鸡狗])', numbers_text)
        
        if number_pairs:
            formatted_numbers = []
            for num, zodiac in number_pairs:
                formatted_numbers.append(f"{num.zfill(2)}{zodiac}")
            
            result = f"{lottery_name}  第 {issue_number} 开奖结果\n" + "\n".join(formatted_numbers)
            return result
            
    except Exception as e:
        print(f"提取{lottery_name}信息时出错: {str(e)}")
    return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    lottery_types = {
        'lam': '老澳门六合彩',
        'xam': '新澳门六合彩',
        'hk': '六合彩',
        'tc': '台湾六合彩'
    }
    
    try:
        # 访问页面
        driver.get('https://akjw09d.48489aaa.com:8800/')
        time.sleep(5)
        
        # 打印页面源码以便调试
        print("页面源码:")
        print(driver.page_source[:500])  # 只打印前500个字符
        
        # 对每种彩票类型进行处理
        for lottery_id, lottery_name in lottery_types.items():
            try:
                result = extract_lottery_info(driver, lottery_name)
                if result:
                    # 保存到对应的txt文件
                    with open(f'{lottery_id}.txt', 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"已保存 {lottery_id} 开奖结果")
                else:
                    print(f"未找到 {lottery_name} 的开奖结果")
            except Exception as e:
                print(f"处理 {lottery_name} 时出错: {str(e)}")
                
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
