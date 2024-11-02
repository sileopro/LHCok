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
        'Referer': 'https://akjw09d.48489aaa.com:8800/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        session = requests.Session()
        base_url = 'https://akjw09d.48489aaa.com:8800'
        
        # 尝试不同的URL路径
        urls_to_try = [
            f'{base_url}',
            f'{base_url}/index',
            f'{base_url}/home',
            f'{base_url}/lottery',
            f'{base_url}/kj/index.html',
            f'{base_url}/lottery/index.html'
        ]
        
        results = {}
        for url in urls_to_try:
            try:
                print(f"\n尝试访问URL: {url}")
                response = session.get(url, headers=headers, verify=False, timeout=10)
                response.encoding = 'utf-8'
                
                print(f"响应状态码: {response.status_code}")
                print(f"响应头: {dict(response.headers)}")
                
                # 检查是否需要重定向
                if response.history:
                    print(f"发生重定向: {response.history}")
                    print(f"最终URL: {response.url}")
                
                # 保存每个URL的响应用于调试
                with open(f'debug_{url.split("/")[-1]}.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # 如果页面包含关键字，进行解析
                if '六合彩' in response.text:
                    print(f"在 {url} 找到可能的结果")
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 查找所有可能包含开奖结果的元素
                    for section in soup.find_all(['div', 'section', 'article']):
                        text = section.get_text(strip=True)
                        
                        # 调试输出
                        if '期' in text or '六合彩' in text:
                            print(f"\n找到相关文本: {text[:200]}")
                        
                        if any(name in text for name in lottery_mapping.values()):
                            period_match = re.search(r'第(\d+)期', text)
                            if period_match:
                                period = period_match.group(1)
                                pairs = re.findall(r'(\d+)([鼠牛虎兔龙蛇马羊猴鸡狗猪])', text)
                                
                                if pairs:
                                    for code, name in lottery_mapping.items():
                                        if name in text:
                                            result_lines = [f"{name}  第 {period} 开奖结果"]
                                            for num, zodiac in pairs:
                                                result_lines.append(f"{num}{zodiac}")
                                            results[code] = "\n".join(result_lines)
                                            print(f"成功解析 {name} 开奖结果")
                
                if results:  # 如果找到了结果，就不再继续尝试其他URL
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"访问 {url} 时出错: {str(e)}")
                continue
        
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
    
    # 设置最大重试次数
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"\n第 {retry_count + 1} 次尝试获取数据")
            results = get_lottery_data()
            
            if results:
                # 保存结果
                for code, result in results.items():
                    with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"已保存 {lottery_mapping[code]} 最新开奖结果到 {code}.txt")
                break  # 如果成功获取数据，跳出重试循环
            else:
                print("未找到任何开奖结果，准备重试...")
                retry_count += 1
                time.sleep(5)  # 等待5秒后重试
                
        except Exception as e:
            print(f"运行出错: {str(e)}")
            retry_count += 1
            time.sleep(5)
    
    # 检查未获取到的彩种
    for code, name in lottery_mapping.items():
        if code not in results:
            print(f"未找到 {name} 开奖结果")

if __name__ == '__main__':
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
