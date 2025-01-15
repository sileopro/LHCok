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
        
        # 先切换到默认内容
        driver.switch_to.default_content()
        
        # 获取所有iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"找到 {len(iframes)} 个iframe")
        
        # 遍历iframe，优先处理较大的iframe
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
                
                # 如果是较小的iframe，跳过
                if len(iframe_source) < 5000:
                    driver.switch_to.default_content()
                    continue
                
                # 打印iframe的HTML结构，用于调试
                print("iframe HTML结构:")
                print(iframe_source[:1000])  # 只打印前1000个字符
                
                # 使用更精确的JavaScript来查找数字元素
                number_elements = driver.execute_script("""
                    function findNumbers() {
                        const numbers = [];
                        const targetTypes = {
                            'lam': '老澳门',
                            'xam': '新澳门',
                            'hk': '香港',
                            'tc': '快乐八'
                        };
                        
                        // 查找包含目标文本的容器
                        const targetText = targetTypes[arguments[0]];
                        let targetContainer = null;
                        
                        // 遍历所有元素查找目标区域
                        const allElements = document.getElementsByTagName('*');
                        for(const el of allElements) {
                            if(el.textContent.includes(targetText)) {
                                // 向上查找可能的容器
                                let parent = el;
                                while(parent && parent.children.length < 10) {
                                    parent = parent.parentElement;
                                }
                                if(parent) {
                                    targetContainer = parent;
                                    break;
                                }
                            }
                        }
                        
                        if(!targetContainer) return numbers;
                        
                        // 在目标容器中查找数字
                        const elements = targetContainer.getElementsByTagName('*');
                        for(const el of elements) {
                            const text = el.textContent.trim();
                            if(/^\\d{1,2}$/.test(text)) {
                                const style = window.getComputedStyle(el);
                                if(style.color !== 'rgb(0, 0, 0)' || style.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                                    numbers.push({
                                        text: text,
                                        color: style.color,
                                        bgColor: style.backgroundColor,
                                        parentText: el.parentElement.textContent
                                    });
                                }
                            }
                        }
                        
                        console.log('找到的数字:', numbers);
                        return numbers;
                    }
                    return findNumbers(arguments[0]);
                """, lottery_type)
                
                if number_elements:
                    print(f"找到 {len(number_elements)} 个数字元素")
                    for num in number_elements:
                        print(f"数字: {num['text']}, 颜色: {num['color']}, 背景色: {num['bgColor']}")
                    
                    # 提取期号
                    issue_match = re.search(r'第(\d+)期', iframe_source)
                    if issue_match:
                        issue = issue_match.group(1)
                        print(f"找到期号: {issue}")
                        
                        # 收集数字
                        numbers = [num['text'] for num in number_elements]
                        
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
                            return result
                
                driver.switch_to.default_content()
                
            except Exception as e:
                print(f"处理iframe时出错: {str(e)}")
                driver.switch_to.default_content()
                continue
        
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
