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
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extract_lottery_info(driver, lottery_name):
    """提取指定彩种的开奖信息"""
    try:
        # 直接查找包含期数和开奖结果的区域
        xpath = f"//div[contains(text(), '{lottery_name}')]/following-sibling::div[contains(text(), '第') and contains(text(), '期')]"
        period_elements = driver.find_elements(By.XPATH, xpath)
        
        for period_elem in period_elements:
            # 获取期数
            period = period_elem.text.split('第')[1].split('期')[0].strip()
            print(f"找到期数: {period}")
            
            # 获取父元素
            parent = period_elem.find_element(By.XPATH, "./..")
            
            # 获取所有数字和生肖
            result_elements = parent.find_elements(By.XPATH, "./div")
            numbers = []
            zodiacs = []
            
            for elem in result_elements:
                text = elem.text.strip()
                if text and not text.startswith('第') and not '开奖' in text:
                    if text.isdigit():
                        numbers.append(text)
                    elif any(zodiac in text for zodiac in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']):
                        zodiacs.append(text)
            
            # 确保找到了数字和生肖
            if numbers and zodiacs and len(numbers) == len(zodiacs):
                result = (
                    f"{lottery_name}  第 {period} 开奖结果\n"
                    f"{' '.join([f'{num}{zodiac}' for num, zodiac in zip(numbers, zodiacs)])}\n"
                )
                print(f"找到完整结果:\n{result}")
                return result
            else:
                print(f"数字: {numbers}")
                print(f"生肖: {zodiacs}")
                
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
        
        # 执行JavaScript来显示内容并等待加载
        driver.execute_script("""
            document.body.style.display = 'block';
            // 等待内容加载
            return new Promise(resolve => {
                let checkContent = setInterval(() => {
                    if (document.body.innerText.includes('六合彩')) {
                        clearInterval(checkContent);
                        resolve(true);
                    }
                }, 500);
                setTimeout(() => {
                    clearInterval(checkContent);
                    resolve(false);
                }, 10000);
            });
        """)
        print("页面内容已显示")
        time.sleep(3)
        
        # 保存页面源码用于调试
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
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
        print("页面内容:")
        print(driver.page_source[:1000])

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
