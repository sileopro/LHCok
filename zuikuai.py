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
        
        base_url = "https://www.hkj.rip/"  # 使用正确的URL
        driver.get(base_url)
        time.sleep(5)
            
        print(f"已访问{lottery_type}页面")
        print(f"当前URL: {driver.current_url}")

        # 根据图片显示的实际布局修改选择器
        try:
            # 获取所有可能包含数字的元素
            number_elements = driver.find_elements(By.CSS_SELECTOR, 'div[style*="background-color"], div[style*="color"]')
            
            # 打印找到的元素数量，用于调试
            print(f"找到 {len(number_elements)} 个可能的数字元素")
            
            # 收集所有数字
            numbers_by_section = {}
            current_section = None
            
            for elem in number_elements:
                try:
                    # 获取元素的完整样式
                    style = elem.get_attribute('style')
                    text = elem.text.strip()
                    
                    # 打印调试信息
                    print(f"元素样式: {style}, 文本: {text}")
                    
                    # 获取父元素内容来确定所属区域
                    parent = driver.execute_script("""
                        let el = arguments[0];
                        let parent = el;
                        for(let i=0; i<5; i++) {
                            if(parent.textContent.includes('期')) {
                                return parent.textContent;
                            }
                            parent = parent.parentElement;
                            if(!parent) break;
                        }
                        return '';
                    """, elem)
                    
                    print(f"父元素内容: {parent}")
                    
                    # 判断所属区域
                    if '老澳门' in parent and lottery_type == 'lam':
                        current_section = 'lam'
                    elif '新澳门' in parent and lottery_type == 'xam':
                        current_section = 'xam'
                    elif '香港' in parent and lottery_type == 'hk':
                        current_section = 'hk'
                    elif '快乐八' in parent and lottery_type == 'tc':
                        current_section = 'tc'
                    
                    # 如果是数字且属于当前彩种，则收集
                    if current_section == lottery_type and text.isdigit():
                        if lottery_type not in numbers_by_section:
                            numbers_by_section[lottery_type] = []
                        numbers_by_section[lottery_type].append(text)
                        
                except Exception as e:
                    print(f"处理元素时出错: {str(e)}")
                    continue
            
            # 处理收集到的数字
            if lottery_type in numbers_by_section and len(numbers_by_section[lottery_type]) >= 7:
                numbers = numbers_by_section[lottery_type]
                
                # 提取期号
                issue_elements = driver.find_elements(By.XPATH, "//div[contains(text(), '期')]")
                issue = None
                for elem in issue_elements:
                    match = re.search(r'第(\d+)期', elem.text)
                    if match:
                        issue = match.group(1)
                        break
                
                if not issue:
                    print("未找到期号")
                    return None
                
                # 提取生肖
                zodiac_chars = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪']
                zodiac = ''
                page_text = driver.page_source
                for z in zodiac_chars:
                    if z in page_text:
                        zodiac = z
                        break
                
                # 格式化结果
                numbers = [num.zfill(2) for num in numbers[:6]]  # 前6个号码
                special_number = numbers_by_section[lottery_type][-1].zfill(2)  # 最后一个作为特码
                
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
