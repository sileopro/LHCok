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
        
        # 保存页面源码用于调试
        page_source = driver.page_source
        print(f"页面源码长度: {len(page_source)}")
        
        # 先切换到默认内容
        driver.switch_to.default_content()
        
        # 获取所有iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"找到 {len(iframes)} 个iframe")
        
        numbers_found = False
        for iframe in iframes:
            try:
                # 切换到iframe
                driver.switch_to.frame(iframe)
                print("切换到iframe")
                
                # 等待页面加载
                time.sleep(2)
                
                # 获取iframe中的源码
                iframe_source = driver.page_source
                print(f"iframe源码长度: {len(iframe_source)}")
                
                # 在iframe中查找数字元素
                number_elements = driver.execute_script("""
                    function findNumbers() {
                        // 获取所有元素
                        const elements = document.getElementsByTagName('*');
                        const numbers = [];
                        
                        for(const el of elements) {
                            // 检查元素是否有样式
                            const style = window.getComputedStyle(el);
                            const text = el.textContent.trim();
                            
                            // 如果元素有颜色样式且包含数字
                            if((style.color !== 'rgb(0, 0, 0)' || style.backgroundColor !== 'rgba(0, 0, 0, 0)') 
                               && /^\\d+$/.test(text)) {
                                numbers.push({
                                    text: text,
                                    style: el.getAttribute('style'),
                                    parent: el.parentElement.textContent
                                });
                            }
                        }
                        return numbers;
                    }
                    return findNumbers();
                """)
                
                if number_elements:
                    print(f"在iframe中找到 {len(number_elements)} 个数字元素")
                    for num in number_elements[:5]:
                        print(f"数字: {num['text']}, 样式: {num['style']}, 父元素: {num['parent']}")
                    
                    # 提取期号
                    issue_match = re.search(r'第(\d+)期', iframe_source)
                    if issue_match:
                        issue = issue_match.group(1)
                        print(f"找到期号: {issue}")
                        
                        # 收集数字
                        numbers = []
                        for num in number_elements:
                            parent_text = num['parent']
                            if ('老澳门' in parent_text and lottery_type == 'lam') or \
                               ('新澳门' in parent_text and lottery_type == 'xam') or \
                               ('香港' in parent_text and lottery_type == 'hk') or \
                               ('快乐八' in parent_text and lottery_type == 'tc'):
                                numbers.append(num['text'])
                        
                        if len(numbers) >= 7:
                            # 提取生肖
                            zodiac_chars = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪']
                            zodiac = next((z for z in zodiac_chars if z in iframe_source), '')
                            
                            # 格式化结果
                            numbers = [num.zfill(2) for num in numbers[:6]]
                            special_number = numbers[-1].zfill(2)
                            issue_short = issue[-3:]
                            
                            result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {zodiac}"
                            print(f"✅ 成功获取{lottery_type}开奖结果：{result}")
                            numbers_found = True
                            return result
                
                # 切换回主框架继续搜索
                driver.switch_to.default_content()
                
            except Exception as e:
                print(f"处理iframe时出错: {str(e)}")
                driver.switch_to.default_content()
                continue
        
        if not numbers_found:
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
