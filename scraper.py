import requests
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

def get_lottery_data(lottery_type):
    """获取彩票数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    
    try:
        # 获取页面内容
        response = requests.get('https://akjw09d.48489aaa.com:8800/', headers=headers, verify=False)
        response.encoding = 'utf-8'
        
        # 保存原始HTML用于调试
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除style标签
        for style in soup.find_all('style'):
            style.decompose()
            
        # 获取页面文本
        text = soup.get_text()
        
        # 使用正则表达式提取开奖信息
        pattern = f'{lottery_mapping[lottery_type]}.*?第(\\d+)期.*?开奖结果.*?((?:\\d+[鼠牛虎兔龙蛇马羊猴鸡狗猪]\\s*)+)'
        match = re.search(pattern, text, re.DOTALL)
        
        if match:
            period = match.group(1)
            result_text = match.group(2)
            
            # 提取数字和生肖对
            pairs = re.findall(r'(\d+)([鼠牛虎兔龙蛇马羊猴鸡狗猪])', result_text)
            
            if pairs:
                result = (
                    f"{lottery_mapping[lottery_type]}  第 {period} 开奖结果\n"
                    f"{' '.join([f'{num}{zodiac}' for num, zodiac in pairs])}\n"
                )
                print(f"找到完整结果:\n{result}")
                return result
                
        print(f"未找到 {lottery_mapping[lottery_type]} 的完整开奖信息")
        print(f"页面文本预览:\n{text[:500]}")
        return None
        
    except Exception as e:
        print(f"获取 {lottery_type} 数据失败: {str(e)}")
        return None

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
        # 获取各彩种结果
        for code, name in lottery_mapping.items():
            print(f"\n正在处理 {name}...")
            result = get_lottery_data(code)
            if result:
                with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"已保存 {name} 开奖结果到 {code}.txt")
            else:
                print(f"未找到 {name} 开奖结果")
                
    except Exception as e:
        print(f"运行出错: {str(e)}")

if __name__ == '__main__':
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
