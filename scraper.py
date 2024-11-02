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

def parse_lottery_result(text):
    """解析开奖结果文本"""
    # 移除多余空格和换行
    text = ' '.join(text.split())
    
    # 提取期数和开奖号码
    match = re.search(r'第\s*(\d+)\s*开奖结果\s*((?:\d+[猪鼠牛虎兔龙蛇马羊猴鸡狗]\s*)+)', text)
    if match:
        issue = match.group(1)
        numbers = match.group(2).strip()
        return issue, numbers
    return None, None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    results = {}
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
        
        # 获取页面内容
        content = driver.page_source
        
        # 对每种彩票类型进行处理
        for lottery_id, lottery_name in lottery_types.items():
            # 查找对应的开奖结果区块
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{lottery_name}')]//ancestor::div[contains(@class, 'lottery-item')]")
            
            for element in elements:
                text = element.text
                if lottery_name in text:
                    issue, numbers = parse_lottery_result(text)
                    if issue and numbers:
                        # 格式化开奖结果
                        result = f"{lottery_name}  第 {issue} 开奖结果\n{numbers}"
                        results[lottery_id] = result
                        
                        # 保存到对应的txt文件
                        with open(f'{lottery_id}.txt', 'w', encoding='utf-8') as f:
                            f.write(result)
                        print(f"已保存 {lottery_id} 开奖结果")
                        break
                        
    except Exception as e:
        print(f"获取开奖结果时出错: {str(e)}")
        
    return results

def main():
    try:
        driver = setup_driver()
        print("浏览器初始化成功")
        
        results = get_lottery_results(driver)
        
        if not results:
            print("未获取到任何开奖结果")
            
    except Exception as e:
        print(f"运行出错: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("浏览器已关闭")

if __name__ == '__main__':
    main()
