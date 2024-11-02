import requests
import json
import time
from datetime import datetime

def get_lottery_data(lottery_type):
    """获取彩票数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Referer': 'https://akjw09d.48489aaa.com:8800/',
        'Origin': 'https://akjw09d.48489aaa.com:8800'
    }
    
    # API端点映射
    api_endpoints = {
        'lam': '/api/lottery/macau/current',  # 老澳门
        'xam': '/api/lottery/newmacau/current',  # 新澳门
        'hk': '/api/lottery/hongkong/current',  # 港彩
        'tc': '/api/lottery/taiwan/current'  # 台湾
    }
    
    try:
        url = f'https://akjw09d.48489aaa.com:8800{api_endpoints[lottery_type]}'
        response = requests.get(url, headers=headers, verify=False)
        print(f"API响应: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                lottery_data = data['data']
                period = lottery_data.get('period', '')
                numbers = lottery_data.get('numbers', [])
                zodiacs = lottery_data.get('zodiacs', [])
                
                if period and numbers and zodiacs:
                    result = (
                        f"{lottery_mapping[lottery_type]}  第 {period} 开奖结果\n"
                        f"{' '.join([f'{num}{zodiac}' for num, zodiac in zip(numbers, zodiacs)])}\n"
                    )
                    return result
                    
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
