from playwright.sync_api import sync_playwright
import time
import re
import os

def get_page():
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context()
        page = context.new_page()
        return playwright, browser, context, page
    except Exception as e:
        print(f"初始化Playwright时出错: {str(e)}")
        return None, None, None, None

def extract_lottery_info(page, lottery_code, lottery_name):
    """提取特定彩票的开奖信息"""
    try:
        # 找到对应的彩票区块
        lottery_div = page.locator(f"#${lottery_code}")
        if not lottery_div:
            print(f"未找到彩票区块: {lottery_code}")
            return None
        
        # 获取期号
        try:
            issue_element = lottery_div.locator(".preDrawIssue")
            issue_number = issue_element.text_content()
            if not issue_number:
                print(f"期号为空")
                return None
                
            issue_number = issue_number.strip()
            print(f"获取到期号: {issue_number}")
            
            match = re.search(r'(\d+)$', issue_number)
            if not match:
                print(f"无法从 {issue_number} 提取期号")
                return None
            issue_short = match.group(1)[-3:]
            print(f"提取的短期号: {issue_short}")
        except Exception as e:
            print(f"处理期号时出错: {str(e)}")
            return None
        
        try:
            number_box = lottery_div.locator(".number-box")
            number_elements = number_box.locator("li")
            
            numbers = []
            special_number = None
            special_zodiac = None
            
            count = number_elements.count()
            for i in range(count):
                elem = number_elements.nth(i)
                if "xgcaddF1" in (elem.get_attribute("class") or ""):
                    continue
                    
                try:
                    number = elem.locator("span").text_content()
                    if not number:
                        continue
                    number = number.zfill(2)
                    
                    zodiac = elem.locator(".animal").text_content()
                    if not zodiac:
                        continue
                        
                    print(f"处理第 {i+1} 个号码: {number} {zodiac}")
                    
                    if i == count - 1:  # 最后一个数字是特码
                        special_number = number
                        special_zodiac = zodiac
                    else:
                        numbers.append(number)
                except Exception as e:
                    print(f"处理单个号码时出错: {str(e)}")
                    continue
            
            if numbers and special_number:
                result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
                print(f"成功生成结果: {result}")
                return result
            else:
                print(f"号码数据不完整: numbers={numbers}, special_number={special_number}")
                return None
                
        except Exception as e:
            print(f"处理号码区块时出错: {str(e)}")
            return None
            
    except Exception as e:
        print(f"提取{lottery_name}信息时出错: {str(e)}")
        return None

def get_lottery_results(page):
    """获取所有彩票开奖结果"""
    lottery_types = {
        'lam': ('AMLHC2', '老澳门六合彩'),
        'xam': ('AMLHC3', '新澳门六合彩'),
        'hk': ('LHC', '六合彩'),
        'tc': ('TWLHC', '台湾六合彩')
    }
    
    try:
        page.goto('https://akjw09d.48489aaa.com:8800/')
        page.wait_for_timeout(5000)  # 等待5秒
        
        results = {}
        for lottery_id, (code, name) in lottery_types.items():
            try:
                result = extract_lottery_info(page, code, name)
                if result:
                    results[lottery_id] = result
                    print(f"已获取 {lottery_id} 开奖结果")
                else:
                    print(f"未找到 {name} 的开奖结果")
            except Exception as e:
                print(f"处理 {name} 时出错: {str(e)}")
                
        return results
                
    except Exception as e:
        print(f"获取开奖结果时出错: {str(e)}")
        return None

def main():
    playwright = browser = context = page = None
    try:
        playwright, browser, context, page = get_page()
        if not all([playwright, browser, context, page]):
            raise Exception("无法初始化浏览器")
            
        print("浏览器初始化成功")
        results = get_lottery_results(page)
        
        if os.environ.get('VERCEL_ENV'):
            return results
            
    except Exception as e:
        print(f"运行出错: {str(e)}")
        if os.environ.get('VERCEL_ENV'):
            return {"error": str(e)}
    finally:
        if page:
            page.close()
        if context:
            context.close()
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
        print("浏览器资源已清理")

if __name__ == '__main__':
    main()
