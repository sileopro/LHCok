import requests
from bs4 import BeautifulSoup
import json

def get_lottery_result(url, lottery_type):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 根据网站实际DOM结构获取数据
        # 这里需要根据实际网站HTML结构调整选择器
        result = soup.select_one('选择器')  
        
        if result:
            # 保存最新一期结果到对应文件
            with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                f.write(result.text.strip())
            print(f'{lottery_type} 更新成功')
    except Exception as e:
        print(f'获取 {lottery_type} 结果失败: {str(e)}')

def main():
    # 定义各彩种URL和对应文件名
    lotteries = {
        'lam': 'https://www.1292.com/澳彩路径',
        'xam': 'https://www.1292.com/新澳彩路径',
        'hk': 'https://www.1292.com/港彩路径'
    }
    
    for lottery_type, url in lotteries.items():
        get_lottery_result(url, lottery_type)

if __name__ == '__main__':
    main() 