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
import random

def get_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 随机 User-Agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
        
        # 使用 CDP 命令来禁用 webdriver 标记
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        return driver
    except Exception as e:
        print(f"设置Chrome驱动时出错: {str(e)}")
        return None

def random_sleep():
    """随机等待一段时间"""
    time.sleep(random.uniform(3, 5))

def extract_lottery_info(driver, lottery_type):
    """提取特定彩票的开奖信息"""
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)
        
        base_url = "https://www.uzzn.com"  # 更新为图片中显示的网址
        driver.get(base_url)
        time.sleep(5)
            
        print(f"已访问{lottery_type}页面")
        print(f"当前URL: {driver.current_url}")

        # 定义彩种名称和对应的标识
        type_info = {
            'lam': {'name': '老澳门', 'text': '老澳门六合彩'},
            'xam': {'name': '新澳门', 'text': '新澳门六合彩'},
            'hk': {'name': '香港彩', 'text': '香港六合彩'},
            'tc': {'name': '快乐八', 'text': '快乐八'}
        }
        
        try:
            # 直接获取所有数字元素
            number_elements = driver.find_elements(By.CSS_SELECTOR, 'div[style*="color"]')
            all_numbers = {}
            current_section = None
            
            for elem in number_elements:
                # 获取父元素的文本，用于判断属于哪个彩种
                parent_text = driver.execute_script("""
                    let el = arguments[0];
                    let parent = el;
                    let text = '';
                    for(let i=0; i<5; i++) {
                        parent = parent.parentElement;
                        if(parent) {
                            text = parent.textContent;
                            if(text.includes('期')) break;
                        }
                    }
                    return text;
                """, elem)
                
                # 判断属于哪个彩种
                for key, info in type_info.items():
                    if info['text'] in parent_text:
                        current_section = key
                        break
                
                if current_section:
                    num = elem.text.strip()
                    if num and num.isdigit():
                        if current_section not in all_numbers:
                            all_numbers[current_section] = []
                        all_numbers[current_section].append(num)
            
            # 处理目标彩种的数据
            if lottery_type in all_numbers and len(all_numbers[lottery_type]) >= 7:
                numbers = all_numbers[lottery_type]
                
                # 提取期号
                issue_text = driver.find_element(By.XPATH, f"//*[contains(text(), '第') and contains(text(), '期')]").text
                issue_match = re.search(r'第(\d+)期', issue_text)
                if not issue_match:
                    print("未找到期号")
                    return None
                    
                issue = issue_match.group(1)
                
                # 提取生肖
                zodiac_chars = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪']
                zodiac = ''
                for z in zodiac_chars:
                    if z in driver.page_source:
                        zodiac = z
                        break
                
                # 格式化结果
                numbers = [num.zfill(2) for num in numbers[:-1]]
                special_number = numbers[-1].zfill(2)
                
                issue_short = issue[-3:]
                result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {zodiac}"
                print(f"✅ 成功获取{lottery_type}开奖结果：{result}")
                return result
            else:
                print(f"警告: {lottery_type} 未获取到足够的号码数据")
                return None
            
        except Exception as e:
            print(f"在提取数据时出错: {str(e)}")
            return None

    except Exception as e:
        print(f"❌ 提取{lottery_type}数据出错: {str(e)}")
        return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    try:
        # 更新初始URL
        driver.get('https://www.hkj.rip/')
        random_sleep()
        print("\n" + "="*80)
        print("浏览器初始化成功")
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        print("="*80 + "\n")
        
        results = {}
        lottery_types = ['lam', 'xam', 'hk', 'tc']
        
        for lottery_type in lottery_types:
            print(f"\n开始获取 {lottery_type} 开奖结果...")
            result = extract_lottery_info(driver, lottery_type)
            if result:
                try:
                    with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                        f.write(result)
                    results[lottery_type] = result
                    print(f"✅ 已成功保存 {lottery_type}.txt")
                except Exception as e:
                    print(f"❌ 保存 {lottery_type}.txt 失败: {str(e)}")
            else:
                print(f"❌ 未能获取 {lottery_type} 开奖结果")
            random_sleep()
                
        return results
                
    except Exception as e:
        print(f"❌ 获取结果出错: {str(e)}")
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
