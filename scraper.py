import requests
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

def get_lottery_data():
    """获取彩票数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://akjw09d.48489aaa.com:8800/',
    }
    
    try:
        session = requests.Session()
        url = 'https://akjw09d.48489aaa.com:8800'
        
        # 获取页面
        response = session.get(url, headers=headers, verify=False, timeout=10)
        response.encoding = 'utf-8'
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = {}
        # 遍历所有开奖结果区域
        for section in soup.find_all('div', class_=lambda x: x and ('lottery' in str(x).lower() or '六合彩' in str(x))):
            # 获取标题文本
            title = section.find(string=lambda text: text and any(name in str(text) for name in lottery_mapping.values()))
            if not title:
                continue
                
            # 获取期号
            period_div = section.find(string=lambda text: text and '第' in str(text) and '期' in str(text))
            if not period_div:
                continue
                
            period_match = re.search(r'第\s*(\d+)\s*期', str(period_div))
            if not period_match:
                continue
                
            period = period_match.group(1)
            
            # 查找数字和生肖
            number_divs = section.find_all(['div', 'span'], string=re.compile(r'\d+'))
            zodiac_divs = section.find_all(['div', 'span'], string=re.compile(r'[鼠牛虎兔龙蛇马羊猴鸡狗猪]'))
            
            pairs = []
            for num_div, zodiac_div in zip(number_divs, zodiac_divs):
                num = re.search(r'\d+', num_div.get_text()).group()
                zodiac = re.search(r'[鼠牛虎兔龙蛇马羊猴鸡狗猪]', zodiac_div.get_text()).group()
                pairs.append((num, zodiac))
            
            if pairs:
                # 确定彩种并保存结果
                for code, name in lottery_mapping.items():
                    if name in str(title):
                        result_lines = [f"{name}  第 {period} 开奖结果"]
                        for num, zodiac in pairs:
                            result_lines.append(f"{num.zfill(2)}{zodiac}")
                        results[code] = "\n".join(result_lines)
                        print(f"找到 {name} 开奖结果")
                        break
        
        return results
        
    except Exception as e:
        print(f"获取数据失败: {str(e)}")
        return {}

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
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
