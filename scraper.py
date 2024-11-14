from playwright.sync_api import sync_playwright
import time
import re
import os

def get_lottery_results():
    """获取所有彩票开奖结果"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        try:
            print("开始访问网页...")
            page.goto('https://akjw09d.48489aaa.com:8800/', wait_until='networkidle')
            time.sleep(5)  # 等待页面加载
            
            lottery_types = {
                'lam': ('AMLHC2', '老澳门六合彩'),
                'xam': ('AMLHC3', '新澳门六合彩'),
                'hk': ('LHC', '六合彩'),
                'tc': ('TWLHC', '台湾六合彩')
            }
            
            results = {}
            for lottery_id, (code, name) in lottery_types.items():
                try:
                    print(f"处理 {name}...")
                    # 获取期号
                    issue = page.locator(f'#{code} .preDrawIssue').text_content()
                    if not issue:
                        print(f"未找到 {name} 期号")
                        continue
                        
                    issue_short = re.search(r'(\d+)$', issue).group(1)[-3:]
                    
                    # 获取号码
                    numbers = []
                    number_elements = page.locator(f'#{code} .number-box li:not(.xgcaddF1) span').all()
                    zodiac_elements = page.locator(f'#{code} .number-box li:not(.xgcaddF1) .animal').all()
                    
                    if len(number_elements) < 7:
                        print(f"未找到足够的号码元素: {len(number_elements)}")
                        continue
                        
                    # 处理前6个号码
                    for num in number_elements[:-1]:
                        numbers.append(num.text_content().zfill(2))
                        
                    # 处理特码
                    special_number = number_elements[-1].text_content().zfill(2)
                    special_zodiac = zodiac_elements[-1].text_content()
                    
                    # 组合结果
                    result = f"第{issue_short}期：{' '.join(numbers)} 特码 {special_number} {special_zodiac}"
                    results[lottery_id] = result
                    
                    # 保存到文件
                    if not os.environ.get('VERCEL_ENV'):
                        with open(f'{lottery_id}.txt', 'w', encoding='utf-8') as f:
                            f.write(result)
                    
                    print(f"成功获取 {name}: {result}")
                    
                except Exception as e:
                    print(f"处理 {name} 时出错: {str(e)}")
                    continue
                    
            return results
                    
        except Exception as e:
            print(f"爬取过程出错: {str(e)}")
            return {"error": str(e)}
        finally:
            browser.close()

def main():
    try:
        results = get_lottery_results()
        return results
    except Exception as e:
        print(f"运行出错: {str(e)}")
        return {"error": str(e)}

if __name__ == '__main__':
    main()
