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
        # 等待页面加载完成
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        random_sleep()
        
        # 使用JavaScript点击图库按钮
        driver.execute_script("""
            var elements = document.getElementsByTagName('span');
            for(var i = 0; i < elements.length; i++) {
                if(elements[i].textContent.includes('图库')) {
                    elements[i].click();
                    break;
                }
            }
        """)
        random_sleep()

        # 点击对应的彩种按钮
        lottery_buttons = {
            'lam': '澳彩',
            'xam': '新澳彩',
            'hk': '港彩',
            'tc': '台彩'
        }
        
        # 使用JavaScript点击彩种按钮
        driver.execute_script(f"""
            var elements = document.getElementsByTagName('div');
            for(var i = 0; i < elements.length; i++) {{
                if(elements[i].textContent.includes('{lottery_buttons[lottery_type]}')) {{
                    elements[i].click();
                    break;
                }}
            }}
        """)
        random_sleep()

        # 打印当前页面源码以便调试
        print(f"当前页面URL: {driver.current_url}")
        print("正在查找开奖信息...")

        # 获取期号
        issue_text = driver.execute_script("""
            var elements = document.getElementsByTagName('div');
            for(var i = 0; i < elements.length; i++) {
                if(elements[i].textContent.includes('第') && elements[i].textContent.includes('期')) {
                    return elements[i].textContent;
                }
            }
            return '';
        """)
        
        if not issue_text:
            raise Exception("未找到期号")
            
        print(f"找到期号文本: {issue_text}")
        match = re.search(r'第(\d+)期', issue_text)
        if not match:
            raise Exception(f"无法从文本'{issue_text}'解析期号")
        issue_short = match.group(1)[-3:]

        # 获取号码和生肖
        numbers_data = driver.execute_script("""
            var numbers = [];
            var zodiac = '';
            var elements = document.querySelectorAll('.circle span, .number span, .zodiac, .animal');
            elements.forEach(function(elem) {
                if(elem.classList.contains('zodiac') || elem.classList.contains('animal')) {
                    zodiac = elem.textContent;
                } else {
                    numbers.push(elem.textContent);
                }
            });
            return {numbers: numbers, zodiac: zodiac};
        """)
        
        if not numbers_data or not numbers_data['numbers']:
            raise Exception("未找到号码")
            
        numbers = [num.strip().zfill(2) for num in numbers_data['numbers'][:-1]]
        special_number = numbers_data['numbers'][-1].strip().zfill(2)
        special_zodiac = numbers_data['zodiac'].strip()

        result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
        print(f"成功获取{lottery_buttons[lottery_type]}开奖结果：{result}")
        return result

    except Exception as e:
        print(f"提取{lottery_type}信息时出错: {str(e)}")
        # 保存页面源码以便调试
        try:
            with open(f'error_{lottery_type}.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"已保存错误页面源码到 error_{lottery_type}.html")
        except:
            pass
        return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    try:
        driver.get('https://6htv99.com/#/home')
        random_sleep()
        print("页面标题:", driver.title)
        print("当前URL:", driver.current_url)
        
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
                random_sleep()
            except Exception as e:
                print(f"处理 {lottery_type} 时出错: {str(e)}")
                driver.get('https://6htv99.com/#/home')
                random_sleep()
                
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
