import requests
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

def get_lottery_data():
    """获取彩票数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cookie': 'chaofancookie=1'
    }
    
    try:
        session = requests.Session()
        url = 'https://akjw09d.48489aaa.com:8800'
        
        response = session.get(url, headers=headers, verify=False)
        response.encoding = 'utf-8'
        
        # 保存原始HTML用于调试
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有开奖结果区域
        results = {}
        for section in soup.find_all('div', class_=lambda x: x and any(name in str(x) for name in ['六合彩', '澳门', '台湾'])):
            title = section.find('div', text=lambda x: x and any(name in str(x) for name in lottery_mapping.values()))
            if title:
                lottery_name = title.text.strip()
                period_elem = section.find('div', text=lambda x: x and '第' in str(x) and '期' in str(x))
                if period_elem:
                    period = re.search(r'第(\d+)期', period_elem.text).group(1)
                    
                    # 查找数字和生肖
                    numbers = []
                    zodiacs = []
                    for elem in section.find_all('div'):
                        text = elem.text.strip()
                        if text.isdigit():
                            numbers.append(text)
                        elif any(zodiac in text for zodiac in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']):
                            zodiacs.append(text)
                    
                    if numbers and zodiacs and len(numbers) == len(zodiacs):
                        result = (
                            f"{lottery_name}  第 {period} 开奖结果\n"
                            f"{' '.join([f'{num}{zodiac}' for num, zodiac in zip(numbers, zodiacs)])}\n"
                        )
                        
                        # 根据彩种名称找到对应的代码
                        for code, name in lottery_mapping.items():
                            if name in lottery_name:
                                results[code] = result
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
        
        # 保存结果
        for code, result in results.items():
            with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"已保存 {lottery_mapping[code]} 开奖结果到 {code}.txt")
            
        # 检查是否有未获取到的彩种
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
