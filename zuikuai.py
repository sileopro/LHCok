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
        
        base_url = "https://www.hkj.rip/"
        driver.get(base_url)
        time.sleep(5)
            
        print(f"已访问{lottery_type}页面")
        print(f"当前URL: {driver.current_url}")

        # 定义彩种名称映射
        type_names = {
            'lam': '老澳门',
            'xam': '新澳门',
            'hk': '香港彩',
            'tc': '快乐八'
        }
        
        target_name = type_names[lottery_type]
        
        # 使用XPath直接查找包含目标文本的元素
        try:
            target_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{target_name}')]")
            print(f"找到目标元素: {target_element.text}")
            
            # 获取父元素
            parent = driver.execute_script("""
                var element = arguments[0];
                var parent = element.parentElement;
                // 向上查找直到找到包含数字的父元素
                while (parent && !parent.textContent.match(/\\d+/)) {
                    parent = parent.parentElement;
                }
                return parent;
            """, target_element)
            
            if not parent:
                print("未找到包含数据的父元素")
                return None
                
            # 获取该区域的所有文本
            text = parent.get_attribute('textContent')
            print(f"找到的文本内容: {text}")
            
            # 提取期号
            issue_match = re.search(r'第(\d+)期', text)
            if not issue_match:
                print("未找到期号")
                return None
                
            issue = issue_match.group(1)
            
            # 获取该区域内所有带颜色样式的元素（通常是号码）
            number_elements = parent.find_elements(By.CSS_SELECTOR, '[style*="color"]')
            numbers = []
            for elem in number_elements:
                num = elem.text.strip()
                if num and num.isdigit():
                    numbers.append(num)
            
            # 提取生肖
            zodiac_chars = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪']
            zodiac = next((z for z in zodiac_chars if z in text), '')
            
            result_data = {
                'issue': f"第{issue}期",
                'numbers': numbers,
                'zodiac': zodiac
            }
            
            print(f"提取的数据: {result_data}")
            
            if not result_data['numbers']:
                print(f"警告: {lottery_type} 未获取到号码数据")
                return None
                
            if len(result_data['numbers']) < 7:
                print(f"错误: {lottery_type} 号码数量不足 ({len(result_data['numbers'])})")
                return None
                
            numbers = [num.zfill(2) for num in result_data['numbers'][:-1]]
            special_number = result_data['numbers'][-1].zfill(2)
            special_zodiac = result_data['zodiac']
            
            issue_short = issue[-3:]
            result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
            print(f"✅ 成功获取{lottery_type}开奖结果：{result}")
            return result
            
        except Exception as e:
            print(f"在查找元素时出错: {str(e)}")
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
