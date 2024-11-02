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
        url = 'https://akjw09d.48489aaa.com:8800'
        
        # 第一次请求获取页面
        response = session.get(url, headers=headers, verify=False)
        response.encoding = 'utf-8'
        
        # 直接从主页获取内容，不再请求背景色和lottery/list
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 保存原始HTML用于调试
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"页面内容预览:\n{response.text[:1000]}")
        
        # 移除style和script标签
        for tag in soup.find_all(['style', 'script']):
            tag.decompose()
            
        # 获取页面文本
        text = soup.get_text()
        print(f"页面文本预览:\n{text[:1000]}")
        
        # 查找所有开奖结果区域
        results = {}
        # 尝试查找包含开奖结果的div元素
        for section in soup.find_all(['div', 'section'], class_=lambda x: x and ('lottery' in x or 'result' in x)):
            text = section.get_text(strip=True)
            if any(name in text for name in lottery_mapping.values()):
                # 查找期数
                period_match = re.search(r'第(\d+)期', text)
                if period_match:
                    period = period_match.group(1)
                    
                    # 查找数字和生肖
                    pairs = re.findall(r'(\d+)([鼠牛虎兔龙蛇马羊猴鸡狗猪])', text)
                    
                    if pairs:
                        # 确定彩种名称
                        for code, name in lottery_mapping.items():
                            if name in text:
                                result_lines = [f"{name}  第 {period} 开奖结果"]
                                for num, zodiac in pairs:
                                    result_lines.append(f"{num}{zodiac}")
                                results[code] = "\n".join(result_lines)
                                print(f"找到 {name} 开奖结果")
                                break
        
        # 如果没有找到结果，尝试其他URL
        if not results:
            alternate_urls = [
                f'{url}/index.html',
                f'{url}/lottery.html',
                f'{url}/results.html'
            ]
            
            for alt_url in alternate_urls:
                try:
                    response = session.get(alt_url, headers=headers, verify=False)
                    response.encoding = 'utf-8'
                    if '六合彩' in response.text:
                        print(f"在 {alt_url} 找到可能的结果")
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # 重复上面的解析逻辑
                        # ... 
                except Exception as e:
                    print(f"尝试访问 {alt_url} 失败: {str(e)}")
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
    
    try:
        # 获取所有彩种结果
        results = get_lottery_data()
        
        # 保存结果，每次覆盖写入最新结果
        for code, result in results.items():
            with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"已保存 {lottery_mapping[code]} 最新开奖结果到 {code}.txt")
            
        # 检查是否有未获取到的彩种
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
