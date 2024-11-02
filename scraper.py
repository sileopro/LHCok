import requests
import re
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup

def get_lottery_data():
    """获取彩票数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://akjw09d.48489aaa.com:8800/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        session = requests.Session()
        base_url = 'https://akjw09d.48489aaa.com:8800'
        
        # 第一步：获取初始页面和cookie
        response = session.get(base_url, headers=headers, verify=False, timeout=10)
        print("初始页面状态码:", response.status_code)
        
        # 第二步：设置必要的cookie
        session.cookies.update({
            'bcolor': '#E9FAFF',
            'selectedBg': 'default'
        })
        
        # 第三步：尝试获取实际数据的API端点
        api_endpoints = [
            f'{base_url}/api/lottery/latest',
            f'{base_url}/api/lottery/current',
            f'{base_url}/lottery/data',
            f'{base_url}/ajax/getLotteryResults'
        ]
        
        results = {}
        for endpoint in api_endpoints:
            try:
                print(f"\n尝试访问API: {endpoint}")
                headers['Content-Type'] = 'application/json'
                response = session.get(endpoint, headers=headers, verify=False, timeout=10)
                print(f"API响应状态码: {response.status_code}")
                print(f"API响应头: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"API返回数据: {json.dumps(data, ensure_ascii=False)[:200]}")
                    except:
                        print("非JSON响应")
                        
                    # 尝试解析返回的内容
                    if '六合彩' in response.text:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        for section in soup.find_all(['div', 'section']):
                            text = section.get_text()
                            for code, name in lottery_mapping.items():
                                if name in text:
                                    period_match = re.search(r'第\s*(\d+)\s*期', text)
                                    if period_match:
                                        period = period_match.group(1)
                                        pairs = re.findall(r'(\d+)\s*([鼠牛虎兔龙蛇马羊猴鸡狗猪])', text)
                                        if len(pairs) >= 7:
                                            result_lines = [f"{name}  第 {period} 开奖结果"]
                                            for num, zodiac in pairs[:7]:
                                                result_lines.append(f"{num.zfill(2)}{zodiac}")
                                            results[code] = "\n".join(result_lines)
                                            print(f"找到 {name} 开奖结果：\n{results[code]}")
            except Exception as e:
                print(f"访问 {endpoint} 出错: {str(e)}")
                continue
        
        # 如果API方式未获取到数据，尝试直接解析HTML
        if not results:
            print("\n尝试解析主页HTML...")
            response = session.get(f'{base_url}/index.html', headers=headers, verify=False)
            response.encoding = 'utf-8'
            
            # 保存HTML用于调试
            with open('debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for section in soup.find_all(['div', 'section']):
                text = section.get_text()
                for code, name in lottery_mapping.items():
                    if name in text:
                        period_match = re.search(r'第\s*(\d+)\s*期', text)
                        if period_match:
                            period = period_match.group(1)
                            pairs = re.findall(r'(\d+)\s*([鼠牛虎兔龙蛇马羊猴鸡狗猪])', text)
                            if len(pairs) >= 7:
                                result_lines = [f"{name}  第 {period} 开奖结果"]
                                for num, zodiac in pairs[:7]:
                                    result_lines.append(f"{num.zfill(2)}{zodiac}")
                                results[code] = "\n".join(result_lines)
                                print(f"找到 {name} 开奖结果：\n{results[code]}")
        
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
