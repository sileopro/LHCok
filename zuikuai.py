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
        
        # 定义内部页面映射
        inner_pages = {
            'lam': '/page/show/lamkj.html',
            'xam': '/page/show/xamkj.html',
            'hk': '/page/show/hkkj.html',
            'tc': '/page/show/kl8kj.html'
        }
        
        # 直接访问内部页面
        inner_url = f"https://www.hkj.rip{inner_pages[lottery_type]}"
        print(f"访问内部页面: {inner_url}")
        driver.get(inner_url)
        time.sleep(5)
        
        # 获取页面内容
        page_source = driver.page_source
        print(f"页面内容长度: {len(page_source)}")
        print("页面内容片段:")
        print(page_source[:500])  # 打印前500个字符用于调试
        
        # 使用更精确的JavaScript查找数字元素
        number_elements = driver.execute_script("""
            function findNumbers() {
                const numbers = [];
                // 查找所有可能包含数字的元素
                const elements = document.querySelectorAll('*');
                
                for (const el of elements) {
                    const text = el.textContent.trim();
                    // 检查是否是1-2位数字
                    if (/^\\d{1,2}$/.test(text)) {
                        const style = window.getComputedStyle(el);
                        const parent = el.parentElement;
                        const parentStyle = parent ? window.getComputedStyle(parent) : null;
                        
                        // 检查元素或其父元素是否有特殊样式
                        if (style.color !== 'rgb(0, 0, 0)' || 
                            style.backgroundColor !== 'rgba(0, 0, 0, 0)' ||
                            (parentStyle && (
                                parentStyle.color !== 'rgb(0, 0, 0)' ||
                                parentStyle.backgroundColor !== 'rgba(0, 0, 0, 0)'
                            ))) {
                            
                            // 获取完整的上下文信息
                            let context = '';
                            let currentEl = el;
                            for (let i = 0; i < 3 && currentEl; i++) {
                                context = currentEl.textContent + ' ' + context;
                                currentEl = currentEl.parentElement;
                            }
                            
                            numbers.push({
                                text: text,
                                style: el.getAttribute('style'),
                                color: style.color,
                                bgColor: style.backgroundColor,
                                context: context.trim(),
                                html: el.outerHTML
                            });
                        }
                    }
                }
                return numbers;
            }
            return findNumbers();
        """)
        
        if number_elements:
            print(f"\n找到 {len(number_elements)} 个数字元素:")
            numbers = []
            for num in number_elements:
                print(f"数字: {num['text']}")
                print(f"颜色: {num['color']}")
                print(f"背景色: {num['bgColor']}")
                print(f"上下文: {num['context']}")
                print(f"HTML: {num['html']}")
                print("---")
                if num['text'].isdigit():
                    numbers.append(num['text'])
            
            if len(numbers) >= 7:
                # 提取期号
                issue_match = re.search(r'第(\d+)期', page_source)
                if not issue_match:
                    print("未找到期号")
                    return None
                
                issue = issue_match.group(1)
                
                # 提取生肖
                zodiac_chars = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪']
                zodiac = next((z for z in zodiac_chars if z in page_source), '')
                
                # 格式化结果
                numbers = [num.zfill(2) for num in numbers[:6]]
                special_number = numbers[6].zfill(2)
                issue_short = issue[-3:]
                
                result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {zodiac}"
                print(f"✅ 成功获取{lottery_type}开奖结果：{result}")
                return result
            else:
                print(f"警告: 数字数量不足 ({len(numbers)})")
        else:
            print("未找到数字元素")
        
        print(f"警告: {lottery_type} 未找到足够的号码数据")
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
