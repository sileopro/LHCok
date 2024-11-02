import requests
import json
import time
from datetime import datetime

def get_lottery_result(lottery_type):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Referer': 'https://www.1292.com/',
        'Origin': 'https://www.1292.com'
    }
    
    # API端点映射
    api_endpoints = {
        'lam': 'https://www.1292.com/api/macau/current',  # 澳彩
        'xam': 'https://www.1292.com/api/newmacau/current',  # 新澳彩
        'hk': 'https://www.1292.com/api/hongkong/current'  # 港彩
    }
    
    try:
        response = requests.get(api_endpoints[lottery_type], headers=headers, timeout=10)
        response.raise_for_status()  # 检查响应状态
        
        print(f"\n当前访问API: {api_endpoints[lottery_type]}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        
        data = response.json()
        
        # 格式化开奖结果
        if data.get('data'):
            lottery_data = data['data']
            period = lottery_data.get('period', '')
            numbers = lottery_data.get('numbers', [])
            draw_time = lottery_data.get('drawTime', '')
            
            # 格式化时间
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
            
            # 保存到文件
            with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f'{lottery_type} 更新成功：\n{result}')
            
        else:
            print(f"未找到 {lottery_type} 的开奖数据")
            print(f"完整响应：{response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f'请求失败 ({lottery_type}): {str(e)}')
    except json.JSONDecodeError as e:
        print(f'JSON解析失败 ({lottery_type}): {str(e)}')
        print(f'原始响应: {response.text}')
    except Exception as e:
        print(f'其他错误 ({lottery_type}): {str(e)}')

def main():
    lottery_types = ['lam', 'xam', 'hk']
    
    for lottery_type in lottery_types:
        print(f'\n正在获取 {lottery_type} 的开奖结果...')
        get_lottery_result(lottery_type)
        time.sleep(2)  # 请求间隔

if __name__ == '__main__':
    main()
