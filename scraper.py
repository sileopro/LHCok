import requests
import json
import time
from datetime import datetime

def get_session_cookies():
    """获取网站cookies"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    session = requests.Session()
    try:
        # 先访问主页获取cookies
        response = session.get('https://www.1292.com', headers=headers)
        print("获取cookies状态码:", response.status_code)
        return session
    except Exception as e:
        print(f"获取cookies失败: {str(e)}")
        return None

def get_lottery_result(session, lottery_type):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.1292.com/',
        'Origin': 'https://www.1292.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # API端点映射
    endpoints = {
        'lam': ('https://www.1292.com/macau', 'https://www.1292.com/api/macau/current'),
        'xam': ('https://www.1292.com/newmacau', 'https://www.1292.com/api/newmacau/current'),
        'hk': ('https://www.1292.com/hongkong', 'https://www.1292.com/api/hongkong/current')
    }
    
    try:
        # 先访问对应的页面
        page_url, api_url = endpoints[lottery_type]
        session.get(page_url, headers=headers)
        
        # 然后请求API
        response = session.get(api_url, headers=headers)
        response.raise_for_status()
        
        print(f"\n当前访问API: {api_url}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text[:200]}")
        
        data = response.json()
        
        if data.get('data'):
            lottery_data = data['data']
            period = lottery_data.get('period', '')
            numbers = lottery_data.get('numbers', [])
            draw_time = lottery_data.get('drawTime', '')
            
            if draw_time:
                try:
                    draw_time = datetime.fromtimestamp(draw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            result = (
                f"期数: {period}\n"
                f"开奖时间: {draw_time}\n"
                f"号码: {' '.join(map(str, numbers)) if numbers else '待开奖'}\n"
            )
            
            with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f'{lottery_type} 更新成功：\n{result}')
            
        else:
            print(f"未找到 {lottery_type} 的开奖数据")
            print(f"完整响应：{response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f'请求失败 ({lottery_type}): {str(e)}')
        if 'response' in locals():
            print(f'响应头: {dict(response.headers)}')
            print(f'响应内容: {response.text}')
    except json.JSONDecodeError as e:
        print(f'JSON解析失败 ({lottery_type}): {str(e)}')
        print(f'原始响应: {response.text}')
    except Exception as e:
        print(f'其他错误 ({lottery_type}): {str(e)}')

def main():
    lottery_types = ['lam', 'xam', 'hk']
    
    # 获取session和cookies
    session = get_session_cookies()
    if not session:
        print("获取session失败")
        return
        
    for lottery_type in lottery_types:
        print(f'\n正在获取 {lottery_type} 的开奖结果...')
        get_lottery_result(session, lottery_type)
        time.sleep(2)

if __name__ == '__main__':
    main()
