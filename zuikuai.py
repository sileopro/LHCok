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
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                driver.get(base_url)
                time.sleep(5)
                break
            except Exception as e:
                print(f"访问主页失败，重试 ({retry_count + 1}/{max_retries})")
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception("访问主页失败次数过多")
                time.sleep(5)
            
        print(f"开始获取 {lottery_type} 开奖结果...")
        
        # 定义内部页面映射
        inner_pages = {
            'lam': '/page/show/lamkj.html',
            'xam': '/page/show/xamkj.html',
            'hk': '/page/show/hkkj.html',
            'tc': '/page/show/kl8kj.html'
        }
        
        # 直接访问内部页面
        inner_url = f"https://www.hkj.rip{inner_pages[lottery_type]}"
        
        retry_count = 0
        while retry_count < max_retries:
            try:
                driver.get(inner_url)
                time.sleep(5)
                break
            except Exception as e:
                print(f"访问内部页面失败，重试 ({retry_count + 1}/{max_retries})")
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception("访问内部页面失败次数过多")
                time.sleep(5)
        
        # 获取页面内容
        page_source = driver.page_source
        
        # 修改查找期号和时间的JavaScript代码
        period_info = driver.execute_script("""
            function findPeriodInfo() {
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (text.includes('期') && text.includes('月') && text.includes('日') && text.includes('图库大全')) {
                        return text;
                    }
                }
                return '';
            }
            return findPeriodInfo();
        """)
        
        # 提取期号和时间
        issue_match = re.search(r'第(\d+)期:(\d+)月(\d+)日.*?(\d+)[点时](\d+)分', period_info)
        if not issue_match:
            print("未能找到有效期号和时间")
            return None
            
        issue = issue_match.group(1)
        next_time = f"{issue_match.group(2)}月{issue_match.group(3)}日 {issue_match.group(4)}点{issue_match.group(5)}分"
        
        # 清空time.txt文件
        if lottery_type == 'lam':  # 只在处理第一个彩种时清空文件
            open('time.txt', 'w', encoding='utf-8').close()
        
        # 保存下期开奖时间到文件
        lottery_names = {
            'lam': '老澳',
            'xam': '新澳',
            'hk': '港彩',
            'tc': '快乐8'
        }
        
        print(f"开始获取{lottery_names[lottery_type]}开奖结果...")
        
        with open('time.txt', 'a', encoding='utf-8') as f:
            f.write(f"{lottery_names[lottery_type]}第{issue}期：{next_time}\n")
        
        # 使用JavaScript查找数字元素
        number_elements = driver.execute_script("""
            function findNumbers() {
                const numbers = [];
                const elements = Array.from(document.querySelectorAll('div[id^="m"], div[id^="s"]'))
                    .sort((a, b) => a.id.localeCompare(b.id));
                
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (/^\\d{1,2}$/.test(text)) {
                        numbers.push(text);
                    }
                }
                return numbers;
            }
            return findNumbers();
        """)
        
        if number_elements and len(number_elements) >= 7:
            # 修改生肖提取逻辑，获取特码的生肖
            zodiac_element = driver.execute_script("""
                const specialBall = document.querySelector('div[id="s1"]');
                if (specialBall && specialBall.parentElement) {
                    const parent = specialBall.parentElement;
                    const nextElement = parent.nextElementSibling;
                    if (nextElement) {
                        const text = nextElement.textContent.trim();
                        if (text.includes('/')) {
                            return text.split('/')[1];
                        }
                    }
                }
                return '';
            """)
            
            # 如果上面的方法失败，尝试另一种方法
            if not zodiac_element:
                zodiac_element = driver.execute_script("""
                    const elements = document.querySelectorAll('.whsx');
                    for (const el of elements) {
                        if (el.previousElementSibling && el.previousElementSibling.id === 's1') {
                            const text = el.textContent.trim();
                            if (text.includes('/')) {
                                return text.split('/')[1];
                            }
                        }
                    }
                    return '';
                """)
            
            # 格式化结果
            numbers = [num.zfill(2) for num in number_elements[:6]]
            special_number = number_elements[6].zfill(2)
            issue_short = issue.zfill(3)[-3:]  # 确保期号是3位数
            
            result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {zodiac_element}"
            print(f"✅ 成功获取开奖结果：{result}")
            
            # 使用正确的文件名
            filename = 'klb.txt' if lottery_type == 'tc' else f'{lottery_type}.txt'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(result)
            
            return result
        else:
            print(f"警告: 数字数量不足")
        
        print(f"警告: 未找到足够的号码数据")
        return None

    except Exception as e:
        print(f"❌ 提取数据出错: {str(e)}")
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
        lottery_names = {
            'lam': '老澳门',
            'xam': '新澳门',
            'hk': '香港',
            'tc': '快乐8'
        }
        
        for lottery_type in lottery_types:
            print(f"\n开始获取{lottery_names[lottery_type]}开奖结果...")
            result = extract_lottery_info(driver, lottery_type)
            if result:
                try:
                    # 使用正确的文件名
                    filename = 'klb.txt' if lottery_type == 'tc' else f'{lottery_type}.txt'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result)
                    results[lottery_type] = result
                    print(f"✅ 已成功保存 {filename}")
                except Exception as e:
                    print(f"❌ 保存文件失败: {str(e)}")
            else:
                print(f"❌ 未能获取开奖结果")
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
