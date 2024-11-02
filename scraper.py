import requests
from bs4 import BeautifulSoup
import time

def get_lottery_result(url, lottery_type):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 获取开奖结果
        if lottery_type == 'hk':
            # 港彩
            result_div = soup.select_one('.hk-lottery-result')
            if result_div:
                period = result_div.select_one('.period').text.strip()
                numbers = result_div.select('.number')
                numbers_text = ' '.join([num.text.strip() for num in numbers])
                result = f"期数：{period}\n号码：{numbers_text}\n"
        
        elif lottery_type == 'xam':
            # 新澳彩
            result_div = soup.select_one('.xam-lottery-result')
            if result_div:
                period = result_div.select_one('.period').text.strip()
                numbers = result_div.select('.number')
                numbers_text = ' '.join([num.text.strip() for num in numbers])
                result = f"期数：{period}\n号码：{numbers_text}\n"
        
        elif lottery_type == 'lam':
            # 澳彩
            result_div = soup.select_one('.lam-lottery-result')
            if result_div:
                period = result_div.select_one('.period').text.strip()
                numbers = result_div.select('.number')
                numbers_text = ' '.join([num.text.strip() for num in numbers])
                result = f"期数：{period}\n号码：{numbers_text}\n"
        
        if result:
            # 保存最新一期结果到对应文件
            with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f'{lottery_type} 更新成功：\n{result}')
        else:
            print(f'未找到 {lottery_type} 的开奖结果')
            
    except Exception as e:
        print(f'获取 {lottery_type} 结果失败: {str(e)}')
        print(f'响应内容: {response.text[:200]}')  # 打印部分响应内容用于调试

def main():
    base_url = 'https://www.1292.com'
    lotteries = {
        'lam': f'{base_url}/lottery/macau',  # 澳彩
        'xam': f'{base_url}/lottery/newmacau',  # 新澳彩
        'hk': f'{base_url}/lottery/hongkong'  # 港彩
    }
    
    for lottery_type, url in lotteries.items():
        print(f'正在获取 {lottery_type} 的开奖结果...')
        get_lottery_result(url, lottery_type)
        time.sleep(2)  # 添加延时，避免请求过快

if __name__ == '__main__':
    main() 