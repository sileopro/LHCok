from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import re

def setup_driver():
    """设置Chrome浏览器"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def select_background(driver):
    """选择背景色"""
    try:
        # 等待页面加载
        time.sleep(5)
        
        # 执行JavaScript来显示内容并点击背景色
        script = """
            // 移除body的display:none
            document.body.style.display = 'block';
            
            // 创建点击事件
            var clickEvent = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            
            // 查找并点击"默认"文本
            var elements = document.getElementsByTagName('*');
            for (var elem of elements) {
                if (elem.textContent.trim() === '默认') {
                    elem.dispatchEvent(clickEvent);
                    return true;
                }
            }
            
            // 如果找不到"默认"，尝试点击"白雪"
            for (var elem of elements) {
                if (elem.textContent.trim() === '白雪') {
                    elem.dispatchEvent(clickEvent);
                    return true;
                }
            }
            
            return false;
        """
        
        result = driver.execute_script(script)
        if result:
            print("已选择背景色")
            time.sleep(3)
            return True
            
        print("未找到背景色选项")
        return False
        
    except Exception as e:
        print(f"选择背景色失败: {str(e)}")
        return False

def extract_lottery_info(driver, lottery_name):
    """提取指定彩种的开奖信息"""
    try:
        # 查找包含开奖结果的文本
        script = f"""
            var results = [];
            var elements = document.getElementsByTagName('*');
            for (var elem of elements) {{
                var text = elem.textContent || '';
                if (text.includes('{lottery_name}') && text.includes('第') && text.includes('期')) {{
                    results.push(text);
                }}
            }}
            return results;
        """
        
        texts = driver.execute_script(script)
        print(f"找到的文本内容: {texts}")
        
        for text in texts:
            # 检查是否包含期数和生肖
            if ('第' in text and '期' in text and 
                any(zodiac in text for zodiac in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪'])):
                
                # 提取期数
                period_match = re.search(r'第(\d+)期', text)
                if period_match:
                    period = period_match.group(1)
                    
                    # 提取数字和生肖
                    pairs = []
                    matches = re.finditer(r'(\d+)([鼠牛虎兔龙蛇马羊猴鸡狗猪])', text)
                    for match in matches:
                        num, zodiac = match.groups()
                        pairs.append(f"{num}{zodiac}")
                    
                    if pairs:
                        result = (
                            f"{lottery_name}  第 {period} 开奖结果\n"
                            f"{' '.join(pairs)}\n"
                        )
                        print(f"找到完整结果:\n{result}")
                        return result
        
        print(f"未找到 {lottery_name} 的完整开奖信息")
        return None
            
    except Exception as e:
        print(f"提取 {lottery_name} 信息时出错: {str(e)}")
        return None

def get_lottery_results(driver):
    """获取所有彩种开奖结果"""
    lottery_mapping = {
        'lam': '老澳门六合彩',
        'xam': '新澳门六合彩',
        'hk': '六合彩',
        'tc': '台湾六合彩'
    }
    
    try:
        # 访问页面
        driver.get('https://akjw09d.48489aaa.com:8800/')
        print("页面加载完成")
        
        # 选择背景色
        if not select_background(driver):
            print("选择背景色失败")
            return
            
        # 等待内容加载
        time.sleep(5)
        
        # 打印页面源码用于调试
        print("页面内容:")
        print(driver.page_source[:1000])
        
        # 获取各彩种结果
        for code, name in lottery_mapping.items():
            print(f"\n正在处理 {name}...")
            result = extract_lottery_info(driver, name)
            if result:
                with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"已保存 {name} 开奖结果到 {code}.txt")
            else:
                print(f"未找到 {name} 开奖结果")
                
    except Exception as e:
        print(f"获取开奖结果时出错: {str(e)}")

def main():
    try:
        driver = setup_driver()
        print("浏览器初始化成功")
        get_lottery_results(driver)
    except Exception as e:
        print(f"运行出错: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("浏览器已关闭")

if __name__ == '__main__':
    main()
