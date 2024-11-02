from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
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
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_lottery_info(driver, lottery_name):
    """提取指定彩种的开奖信息"""
    try:
        # 查找包含开奖结果的文本
        elements = driver.find_elements(By.XPATH, "//div[contains(text(), '开奖结果')]")
        
        for element in elements:
            # 获取父元素的文本内容
            parent = element.find_element(By.XPATH, "./..")
            text = parent.text
            
            # 检查是否包含期数和生肖
            if ('第' in text and '期' in text and 
                any(zodiac in text for zodiac in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪'])):
                
                # 提取期数
                period_match = re.search(r'第(\d+)期', text)
                if period_match:
                    period = period_match.group(1)
                    
                    # 提取数字和生肖
                    result_text = text.split('开奖结果')[1].strip()
                    pairs = []
                    
                    # 使用正则表达式匹配数字和生肖
                    matches = re.finditer(r'(\d+)([鼠牛虎兔龙蛇马羊猴鸡狗猪])', result_text)
                    for match in matches:
                        num, zodiac = match.groups()
                        pairs.append(f"{num}{zodiac}")
                    
                    if pairs:
                        result = (
                            f"{lottery_name}  第 {period} 开奖结果\n"
                            f"{' '.join(pairs)}\n"
                        )
                        print(f"找到完整结果:\n{result}")
                        return result
        
        print(f"未找到 {lottery_name} 的完整开奖信息")
        return None
            
    except Exception as e:
        print(f"提取 {lottery_name} 信息时出错: {str(e)}")
        return None

def get_lottery_results(driver):
    """获取所有彩种开奖结果"""
    lottery_mapping = {
        'lam': '老澳门六合彩',
        'xam': '新澳门六合彩',
        'hk': '六合彩',
        'tc': '台湾六合彩'
    }
    
    try:
        # 访问页面
        driver.get('https://akjw09d.48489aaa.com:8800/')
        print("页面加载完成")
        time.sleep(5)
        
        # 执行JavaScript来显示内容
        driver.execute_script("""
            document.body.style.display = 'block';
            // 移除所有style标签
            document.querySelectorAll('style').forEach(s => s.remove());
        """)
        time.sleep(3)
        
        # 获取各彩种结果
        for code, name in lottery_mapping.items():
            print(f"\n正在处理 {name}...")
            result = extract_lottery_info(driver, name)
            if result:
                with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"已保存 {name} 开奖结果到 {code}.txt")
            else:
                print(f"未找到 {name} 开奖结果")
                
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
