import requests
import json
import time
from datetime import datetime
import random

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    return random.choice(user_agents)

def get_lottery_result(lottery_type):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': 'https://www.1292.com',
        'Referer': 'https://www.1292.com/',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }

    # API端点
    api_urls = {
        'lam': 'https://www.1292.com/api/macau/history',
        'xam': 'https://www.1292.com/api/newmacau/history',
        'hk': 'https://www.1292.com/api/hongkong/history'
    }

    try:
        # 先获取cookies
        session = requests.Session()
        session.get('https://www.1292.com', headers=headers, timeout=30)
        
        print(f"\n正在获取 {lottery_type} 的开奖结果...")
        
        # 获取历史数据
        response = session.get(api_urls[lottery_type], headers=headers, timeout=30)
        print(f"API响应状态码: {response.status_code}")
        print(f"API响应头: {dict(response.headers)}")
        print(f"API响应内容: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                latest = data['data'][0]  # 获取最新一期
                
                # 格式化结果
                result = (
                    f"期数: {latest.get('period', '未知')}\n"
                    f"开奖时间: {datetime.fromtimestamp(latest.get('drawTime', 0)/1000).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"号码: {' '.join(map(str, latest.get('numbers', [])))}\n"
                )
                
                # 保存结果
                with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"成功保存 {lottery_type} 开奖结果:\n{result}")
                
            else:
                print(f"未找到 {lottery_type} 的开奖数据")
                print(f"完整响应: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"请求失败 ({lottery_type}): {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON解析失败 ({lottery_type}): {str(e)}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"其他错误 ({lottery_type}): {str(e)}")

def main():
    lottery_types = ['lam', 'xam', 'hk']
    
    for lottery_type in lottery_types:
        get_lottery_result(lottery_type)
        time.sleep(3)  # 请求间隔

if __name__ == '__main__':
    main()
