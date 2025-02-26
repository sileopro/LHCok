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
        
        # 点击图库按钮
        try:
            gallery_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='图库']"))
            )
            driver.execute_script("arguments[0].click();", gallery_button)
        except:
            gallery_clicked = driver.execute_script("""
                var elements = document.querySelectorAll('span, div');
                for(var i = 0; i < elements.length; i++) {
                    if(elements[i].textContent.trim() === '图库') {
                        elements[i].click();
                        return true;
                    }
                }
                return false;
            """)
            if not gallery_clicked:
                return None
        
        random_sleep()

        # 点击对应的彩种按钮
        lottery_buttons = {
            'lam': '澳彩',
            'xam': '新澳彩',
            'hk': '港彩',
            'tc': '台彩'
        }
        
        # 使用多种方式尝试点击
        button_clicked = False
        
        # 方法1：直接点击
        try:
            button = driver.find_element(By.XPATH, f"//div[text()='{lottery_buttons[lottery_type]}']")
            driver.execute_script("arguments[0].click();", button)
            button_clicked = True
        except:
            pass
        
        # 方法2：使用部分文本匹配
        if not button_clicked:
            try:
                button = driver.find_element(By.XPATH, f"//div[contains(text(), '{lottery_buttons[lottery_type]}')]")
                driver.execute_script("arguments[0].click();", button)
                button_clicked = True
            except:
                pass
        
        # 方法3：使用JavaScript点击
        if not button_clicked:
            button_clicked = driver.execute_script(f"""
                var elements = document.getElementsByTagName('div');
                for(var i = 0; i < elements.length; i++) {{
                    if(elements[i].textContent.includes('{lottery_buttons[lottery_type]}')) {{
                        elements[i].click();
                        return true;
                    }}
                }}
                return false;
            """)
        
        if not button_clicked:
            return None
            
        print(f"已点击{lottery_buttons[lottery_type]}按钮")
        time.sleep(3)

        # 获取号码和生肖
        result_data = driver.execute_script("""
            function extractData() {
                try {
                    // 获取期号
                    var issueText = '';
                    var elements = document.getElementsByTagName('div');
                    for(var i = 0; i < elements.length; i++) {
                        var text = elements[i].textContent;
                        if(text.includes('第') && text.includes('期') && text.includes('最新开奖结果')) {
                            console.log('找到期号文本:', text);
                            // 提取期号
                            var match = text.match(/第(\\d+)期/);
                            if(match) {
                                issueText = match[0];
                                break;
                            }
                        }
                    }
                    
                    // 获取号码和生肖
                    var numbers = [];
                    var zodiac = '';
                    var elements = document.getElementsByTagName('div');
                    var processedNumbers = new Set(); // 用于去重
                    
                    for(var i = 0; i < elements.length; i++) {
                        var text = elements[i].textContent.trim();
                        // 检查是否包含数字和生肖
                        if(text.includes('/')) {
                            var parts = text.split('/');
                            if(parts.length == 2) {
                                var num = parts[0].match(/\\d+/);
                                if(num && !processedNumbers.has(num[0])) {
                                    numbers.push(num[0]);
                                    processedNumbers.add(num[0]); // 添加到已处理集合
                                    if(numbers.length == 7) {  // 最后一个数字的生肖
                                        zodiac = parts[0].replace(/\\d+/g, '').trim(); // 获取数字前面的生肖
                                    }
                                }
                            }
                        }
                    }
                    
                    console.log('找到号码:', numbers);
                    console.log('找到生肖:', zodiac);
                    
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
        return None

def get_lottery_results(driver):
    """获取所有彩票开奖结果"""
    try:
        driver.get('https://6htv99.com/#/home')
        random_sleep()
        print("\n" + "="*80)
        print("浏览器初始化成功")
        print(f"页面标题: {driver.title}")
        print(f"当前URL: {driver.current_url}")
        print("="*80 + "\n")
        
        results = {}
        lottery_types = ['lam', 'xam', 'hk']
        
        for lottery_type in lottery_types:
            result = extract_lottery_info(driver, lottery_type)
            if result:
                with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                results[lottery_type] = result
                print(f"✅ 已保存 {lottery_type} 开奖结果")
            driver.get('https://6htv99.com/#/home')
            random_sleep()
                
        return results
                
    except Exception as e:
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
