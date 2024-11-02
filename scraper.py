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
        
        # 打印页面内容，用于调试
        print(f"\n当前访问URL: {url}")
        print("页面内容预览:")
        print(soup.prettify()[:1000])  # 打印前1000个字符用于调试
        
        result = None  # 初始化result变量
        
        # 获取所有的div标签，用于调试
        all_divs = soup.find_all('div')
        print(f"\n找到的div标签数量: {len(all_divs)}")
        
        # 尝试查找包含开奖信息的元素
        if lottery_type == 'hk':
            # 港彩 - 尝试多个可能的选择器
            result_div = (
                soup.select_one('.lottery-result') or 
                soup.select_one('.kj-result') or
                soup.select_one('[class*="result"]') or  # 包含"result"的class
                soup.select_one('[class*="lottery"]')    # 包含"lottery"的class
            )
            
            if result_div:
                print("找到港彩结果区域:", result_div.text[:100])
                # 尝试提取期数和号码
                result = f"港彩\n{result_div.text.strip()}\n"
            
        elif lottery_type == 'xam':
            # 新澳彩
            result_div = (
                soup.select_one('.lottery-result') or 
                soup.select_one('.kj-result') or
                soup.select_one('[class*="result"]')
            )
            
            if result_div:
                print("找到新澳彩结果区域:", result_div.text[:100])
                result = f"新澳彩\n{result_div.text.strip()}\n"
            
        elif lottery_type == 'lam':
            # 澳彩
            result_div = (
                soup.select_one('.lottery-result') or 
                soup.select_one('.kj-result') or
                soup.select_one('[class*="result"]')
            )
            
            if result_div:
                print("找到澳彩结果区域:", result_div.text[:100])
                result = f"澳彩\n{result_div.text.strip()}\n"
        
        if result:
            # 保存最新一期结果到对应文件
            with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f'{lottery_type} 更新成功：\n{result}')
        else:
            print(f'未找到 {lottery_type} 的开奖结果')
            # 保存完整的HTML以供分析
            with open(f'debug_{lottery_type}.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
    except Exception as e:
        print(f'获取 {lottery_type} 结果失败: {str(e)}')
        if 'response' in locals():
            print(f'响应状态码: {response.status_code}')
            print(f'响应内容: {response.text[:500]}')

def main():
    base_url = 'https://www.1292.com'
    lotteries = {
        'lam': f'{base_url}/lottery/macau',  # 澳彩
        'xam': f'{base_url}/lottery/newmacau',  # 新澳彩
        'hk': f'{base_url}/lottery/hongkong'  # 港彩
    }
    
    for lottery_type, url in lotteries.items():
        print(f'\n正在获取 {lottery_type} 的开奖结果...')
        get_lottery_result(url, lottery_type)
        time.sleep(3)  # 增加延时到3秒

if __name__ == '__main__':
    main() 
