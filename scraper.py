import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_lottery_data():
    """获取彩票数据"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无界面模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
    
    try:
        print("初始化浏览器...")
        driver = webdriver.Chrome(options=chrome_options)
        url = 'https://akjw09d.48489aaa.com:8800'
        
        print(f"访问网页: {url}")
        driver.get(url)
        
        # 等待页面加载
        time.sleep(5)
        
        print("页面标题:", driver.title)
        print("当前URL:", driver.current_url)
        print("页面内容:", driver.page_source[:1000])
        
        results = {}
        
        # 等待并查找所有可能包含开奖结果的元素
        wait = WebDriverWait(driver, 10)
        sections = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div')))
        
        for section in sections:
            try:
                text = section.text
                if not text:
                    continue
                    
                for code, name in lottery_mapping.items():
                    if name in text:
                        # 查找期号
                        period_match = re.search(r'第\s*(\d+)\s*期', text)
                        if period_match:
                            period = period_match.group(1)
                            
                            # 查找数字和生肖
                            pairs = re.findall(r'(\d+)\s*([鼠牛虎兔龙蛇马羊猴鸡狗猪])', text)
                            
                            if len(pairs) >= 7:
                                result_lines = [f"{name}  第 {period} 开奖结果"]
                                for num, zodiac in pairs[:7]:
                                    result_lines.append(f"{num.zfill(2)}{zodiac}")
                                results[code] = "\n".join(result_lines)
                                print(f"找到 {name} 开奖结果：\n{results[code]}")
            except Exception as e:
                print(f"处理元素时出错: {str(e)}")
                continue
        
        return results
        
    except Exception as e:
        print(f"获取数据失败: {str(e)}")
        return {}
    finally:
        try:
            driver.quit()
        except:
            pass

def main():
    """主函数"""
    global lottery_mapping
    lottery_mapping = {
        'lam': '老澳门六合彩',
        'xam': '新澳门六合彩',
        'hk': '六合彩',
        'tc': '台湾六合彩'
    }
    
    try:
        # 获取所有彩种结果
        results = get_lottery_data()
        
        if results:
            # 保存结果
            for code, result in results.items():
                with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"已保存 {lottery_mapping[code]} 最新开奖结果到 {code}.txt")
        else:
            print("未找到任何开奖结果")
            
        # 检查未获取到的彩种
        for code, name in lottery_mapping.items():
            if code not in results:
                print(f"未找到 {name} 开奖结果")
                
    except Exception as e:
        print(f"运行出错: {str(e)}")

if __name__ == '__main__':
    main()
