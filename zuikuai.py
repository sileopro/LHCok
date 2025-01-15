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
        
        # 新网站的彩种映射和对应的URL
        lottery_urls = {
            'lam': 'https://www.hkj.rip/macau/',
            'xam': 'https://www.hkj.rip/macau-new/',
            'hk': 'https://www.hkj.rip/hk/',
            'tc': 'https://www.hkj.rip/taiwan/'
        }
        
        # 直接访问对应彩种的URL
        driver.get(lottery_urls[lottery_type])
        random_sleep()
            
        print(f"已访问{lottery_type}页面")

        # 获取号码和生肖
        result_data = driver.execute_script("""
            function extractData() {
                try {
                    // 获取期号
                    var issueText = '';
                    var issueElements = document.querySelectorAll('div, span');
                    for(var el of issueElements) {
                        if(el.textContent.includes('期')) {
                            issueText = el.textContent;
                            break;
                        }
                    }
                    
                    // 获取号码
                    var numbers = [];
                    var numberElements = document.querySelectorAll('.number, .ball');
                    numberElements.forEach(function(el) {
                        var num = el.textContent.trim();
                        if(num && !isNaN(num)) numbers.push(num);
                    });
                    
                    // 获取特码生肖
                    var zodiac = '';
                    var zodiacElements = document.querySelectorAll('div, span');
                    for(var el of zodiacElements) {
                        var text = el.textContent.trim();
                        if(['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪'].includes(text)) {
                            zodiac = text;
                            break;
                        }
                    }
                    
                    return {
                        issue: issueText,
                        numbers: numbers,
                        zodiac: zodiac
                    };
                } catch(e) {
                    console.error('提取数据时出错:', e);
                    return null;
                }
            }
            return extractData();
        """)
        
        if not result_data:
            return None
            
        # 解析期号
        match = re.search(r'第(\d+)期', result_data['issue'])
        if not match:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            match = re.search(r'第(\d+)期最新开奖结果', page_text)
            if not match:
                return None
        issue_short = match.group(1)[-3:]
        
        # 处理号码
        if len(result_data['numbers']) < 7:
            return None
            
        numbers = [num.zfill(2) for num in result_data['numbers'][:-1]]
        special_number = result_data['numbers'][-1].zfill(2)
        special_zodiac = result_data['zodiac']

        result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
        print(f"成功获取{lottery_type}开奖结果：{result}")
        return result

    except Exception as e:
        print(f"提取数据出错: {str(e)}")
        return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    try:
        driver.get('https://www.hkj.rip')
        random_sleep()
        print("\n" + "="*80)
        print("浏览器初始化成功")
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        print("="*80 + "\n")
        
        results = {}
        lottery_types = ['lam', 'xam', 'hk', 'tc']
        
        for lottery_type in lottery_types:
            result = extract_lottery_info(driver, lottery_type)
            if result:
                with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                results[lottery_type] = result
                print(f"✅ 已保存 {lottery_type} 开奖结果")
            random_sleep()
                
        return results
                
    except Exception as e:
        print(f"获取结果出错: {str(e)}")
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
