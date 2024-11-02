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
        
        # 模拟点击背景色
        background_data = {
            'bcolor': '#E9FAFF',  # 默认背景色
            'text': '默认',
            'type': 'background'
        }
        
        # 发送背景色选择请求
        bg_url = f'{url}/ajax/setBackground'
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        response = session.post(bg_url, data=background_data, headers=headers, verify=False)
        print(f"背景色设置响应: {response.text[:200]}")
        
        # 设置cookie
        cookies = {
            'chaofancookie': '1',
            'bcolor': '#E9FAFF',
            'selectedBg': 'default',
            'JSESSIONID': session.cookies.get('JSESSIONID', '')
        }
        session.cookies.update(cookies)
        
        # 获取内容
        headers['Accept'] = '*/*'
        response = session.get(f'{url}/lottery/list', headers=headers, cookies=cookies, verify=False)
        response.encoding = 'utf-8'
        
        # 保存原始HTML用于调试
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"页面内容预览:\n{response.text[:1000]}")
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除style和script标签
        for tag in soup.find_all(['style', 'script']):
            tag.decompose()
            
        # 获取页面文本
        text = soup.get_text()
        print(f"页面文本预览:\n{text[:1000]}")
        
        # 查找所有开奖结果区域
        results = {}
        for section in soup.find_all('div', recursive=True):
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
                                # 修改结果格式，每个数字生肖对单独一行
                                result_lines = [f"{name}  第 {period} 开奖结果"]
                                for num, zodiac in pairs:
                                    result_lines.append(f"{num}{zodiac}")
                                results[code] = "\n".join(result_lines)
                                print(f"找到 {name} 开奖结果")
                                break
        
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
