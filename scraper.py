import requests
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup

def get_lottery_data():
    """获取彩票数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://akjw09d.48489aaa.com:8800/',
    }
    
    try:
        session = requests.Session()
        url = 'https://akjw09d.48489aaa.com:8800'
        
        # 获取页面
        response = session.get(url, headers=headers, verify=False, timeout=10)
        response.encoding = 'utf-8'
        
        # 保存原始HTML用于调试
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"页面内容预览:\n{response.text[:1000]}")
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = {}
        # 查找所有可能的开奖结果区域
        sections = soup.find_all('div', recursive=True)
        
        for section in sections:
            # 查找包含彩种名称的文本
            for code, name in lottery_mapping.items():
                if name in section.get_text():
                    # 在同一区域内查找期号
                    period_text = section.find(string=re.compile(r'第.*期'))
                    if period_text:
                        period_match = re.search(r'第\s*(\d+)\s*期', period_text)
                        if period_match:
                            period = period_match.group(1)
                            
                            # 查找所有数字和生肖
                            text = section.get_text()
                            pairs = []
                            
                            # 使用正则表达式查找所有数字和生肖对
                            all_matches = re.finditer(r'(\d+)\s*([鼠牛虎兔龙蛇马羊猴鸡狗猪])', text)
                            for match in all_matches:
                                num, zodiac = match.groups()
                                pairs.append((num, zodiac))
                            
                            if len(pairs) >= 7:  # 确保找到足够的数字和生肖对
                                result_lines = [f"{name}  第 {period} 开奖结果"]
                                for num, zodiac in pairs[:7]:  # 只取前7个
                                    result_lines.append(f"{num.zfill(2)}{zodiac}")
                                results[code] = "\n".join(result_lines)
                                print(f"找到 {name} 开奖结果：\n{results[code]}")
                            
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
