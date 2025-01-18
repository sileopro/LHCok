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
            
        print(f"✅ 开始获取 {lottery_type} 开奖结果...")
        
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
        
        # 修改查找期号和时间的JavaScript代码，获取当前期号
        period_info = driver.execute_script("""
            function findPeriodInfo() {
                // 首先尝试获取开奖结果区域的期号
                const resultArea = document.querySelector('.kj-result, .kj-content');
                if (resultArea) {
                    const periodText = resultArea.textContent.match(/第(\\d+)期/);
                    if (periodText) {
                        return periodText[0];
                    }
                }
                
                // 如果上面失败，则查找包含开奖结果的元素
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    // 优先匹配包含开奖结果的期号
                    if (text.includes('开奖结果') && text.match(/第\\d+期/)) {
                        const match = text.match(/第(\\d+)期/);
                        if (match) return match[0];
                    }
                }
                
                // 如果还是找不到，返回空字符串
                return '';
            }
            return findPeriodInfo();
        """)
        
        # 修改获取开奖时间信息的JavaScript代码
        time_info = driver.execute_script("""
            function findTimeInfo() {
                // 针对快乐8特殊处理
                if (window.location.href.includes('kl8kj')) {
                    const elements = document.querySelectorAll('*');
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        // 匹配快乐8的时间格式
                        if (text.includes('开奖时间') && text.includes('期')) {
                            return text;
                        }
                    }
                }
                
                // 其他彩种的处理逻辑
                const timeArea = document.querySelector('.kj-time, .time-info');
                if (timeArea) {
                    const text = timeArea.textContent.trim();
                    if (text.match(/第\\d+期.*?\\d+月\\d+日.*?\\d+[点时]\\d+分/)) {
                        return text;
                    }
                }
                
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if (text.includes('开奖时间') || 
                        text.match(/第\\d+期.*?\\d+月\\d+日.*?\\d+[点时]\\d+分/)) {
                        return text;
                    }
                }
                return '';
            }
            return findTimeInfo();
        """)
        
        # 针对快乐8特殊处理期号和时间的提取
        if lottery_type == 'tc':
            issue_match = re.search(r'第(\d+)期', time_info)
            time_match = re.search(r'(\d{2}):(\d{2})', time_info)
            
            if issue_match and time_match:
                issue = issue_match.group(1)
                current_time = f"开奖时间 {time_match.group(0)}"
            else:
                print(f"❌ 未能找到快乐8的期号或时间: {time_info}")
                return None
        else:
            # 其他彩种的处理保持不变
            issue_match = re.search(r'第(\d+)期', period_info)
            time_match = re.search(r'(\d{1,2})月(\d{1,2})日.*?(\d{1,2})[点时](\d{1,2})分', time_info)
            
            if not issue_match or not time_match:
                print(f"❌ 未能找到有效期号或时间: {period_info} | {time_info}")
                return None
                
            issue = issue_match.group(1)
            month = time_match.group(1).zfill(2)
            day = time_match.group(2).zfill(2)
            current_time = f"{month}月{day}日 {time_match.group(3)}点{time_match.group(4)}分"

        # 获取下一期开奖时间信息
        next_period_info = driver.execute_script("""
            function findNextPeriodInfo() {
                // 查找包含"下期开奖"或"下期时间"的元素
                const elements = document.querySelectorAll('*');
                for (const el of elements) {
                    const text = el.textContent.trim();
                    if ((text.includes('下期开奖') || text.includes('下期时间')) && 
                        text.match(/第\\d+期.*?\\d+月\\d+日.*?\\d+[点时]\\d+分/)) {
                        return text;
                    }
                }
                return '';
            }
            return findNextPeriodInfo();
        """)
        
        # 分别提取下一期期号和时间
        next_issue_match = re.search(r'第(\d+)期', next_period_info)
        next_time_match = re.search(r'(\d{1,2})月(\d{1,2})日.*?(\d{1,2})[点时](\d{1,2})分', next_period_info)
        
        # 设置下一期信息
        if next_issue_match and next_time_match:
            next_issue = next_issue_match.group(1)
            next_month = next_time_match.group(1).zfill(2)
            next_day = next_time_match.group(2).zfill(2)
            next_time = f"{next_month}月{next_day}日 {next_time_match.group(3)}点{next_time_match.group(4)}分"
        else:
            # 如果找不到下一期信息，则基于当前期计算下一期
            current_issue = int(issue)
            next_issue = str(current_issue + 1).zfill(3)
            next_time = current_time
            
        # 保存开奖时间信息到 time.txt
        lottery_names = {
            'lam': '老澳',
            'xam': '新澳',
            'hk': '港彩',
            'tc': '快乐8'
        }
        
        try:
            if lottery_type == 'lam':
                with open('time.txt', 'w', encoding='utf-8') as f:
                    f.write(f"{lottery_names[lottery_type]}第{next_issue}期：{next_time}\n")
            else:
                with open('time.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{lottery_names[lottery_type]}第{next_issue}期：{next_time}\n")
            print(f"✅ 已更新 {lottery_names[lottery_type]} 开奖时间信息")
        except Exception as e:
            print(f"❌ 保存时间信息失败: {str(e)}")
        
        # 修改号码获取的JavaScript代码，添加快乐8特殊处理
        number_elements = driver.execute_script("""
            function findNumbers() {
                // 针对快乐8特殊处理
                if (window.location.href.includes('kl8kj')) {
                    const numbers = [];
                    const elements = document.querySelectorAll('.kj-ball');
                    elements.forEach(el => {
                        const num = el.textContent.trim();
                        if (/^\\d{1,2}$/.test(num)) {
                            numbers.push(num);
                        }
                    });
                    return numbers;
                }
                
                // 其他彩种的处理保持不变
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
        
        if number_elements:
            if lottery_type == 'tc':
                # 快乐8的结果格式化
                numbers = [num.zfill(2) for num in number_elements[:20]]  # 快乐8通常有20个号码
                issue_short = issue.zfill(3)[-3:]
                result = f"第{issue_short}期：{' '.join(numbers)}"
            else:
                # 其他彩种保持原有格式
                numbers = [num.zfill(2) for num in number_elements[:6]]
                special_number = number_elements[6].zfill(2)
                issue_short = issue.zfill(3)[-3:]
                
                # 获取生肖（快乐8不需要）
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
                
                result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {zodiac_element}"
            
            print(f"✅ 成功获取开奖结果：{result}")
            return result
            
        print(f"❌ 警告: 未找到足够的号码数据")
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
            print("="*80)  # 只保留一条分割线
            print(f"\n开始获取{lottery_names[lottery_type]}开奖结果...")
            result = extract_lottery_info(driver, lottery_type)
            if result:
                try:
                    # 使用正确的文件名，快乐8保存为klb.txt
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
            raise Exception("❌ 浏览器初始化失败")
            
        print("✅ 浏览器初始化成功")
        results = get_lottery_results(driver)
        
        # 调整 time.txt 内容显示顺序
        try:
            print("\n✅ time.txt 读取成功")
            print("=== time.txt 内容 ===")
            with open('time.txt', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(content)
            print("=== time.txt 内容结束 ===\n")
        except Exception as e:
            print(f"❌ 读取 time.txt 失败: {str(e)}\n")
        
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
