import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

def get_lottery_result(lottery_type):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }

    try:
        print(f"\n正在获取 {lottery_type} 的开奖结果...")
        
        # 获取页面内容
        response = requests.get('https://akjw09d.48489aaa.com:8800/', headers=headers, verify=False)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 打印页面内容，用于调试
            print("页面内容预览:")
            print(response.text[:1000])
            
            # 打印所有div的class属性
            print("\n所有div的class:")
            for div in soup.find_all('div'):
                if div.get('class'):
                    print(f"Class: {' '.join(div.get('class'))}")
            
            # 打印所有包含数字的元素
            print("\n包含数字的元素:")
            for elem in soup.find_all(text=lambda t: t and any(c.isdigit() for c in t)):
                print(f"Text: {elem.strip()}")
            
            # 打印所有包含"期"字的元素
            print("\n包含'期'的元素:")
            for elem in soup.find_all(text=lambda t: t and '期' in t):
                print(f"Text: {elem.strip()}")
            
            # 尝试查找开奖结果
            # 先查找包含期数的元素
            period_elements = soup.find_all(text=lambda t: t and '期' in t)
            if period_elements:
                print("\n找到期数元素:")
                for elem in period_elements:
                    print(f"期数文本: {elem.strip()}")
                    # 查找这个元素附近的数字
                    parent = elem.parent
                    if parent:
                        numbers = parent.find_all(text=lambda t: t and t.strip().isdigit())
                        print(f"相关数字: {[n.strip() for n in numbers]}")
            
            # 保存页面源码用于分析
            with open(f'debug_{lottery_type}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\n已保存完整页面源码到 debug_{lottery_type}.html")
            
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            
    except Exception as e:
        print(f"获取 {lottery_type} 结果失败: {str(e)}")
        if 'response' in locals():
            print(f"响应内容: {response.text[:500]}")

def main():
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    lottery_types = ['lam', 'xam', 'hk']
    
    for lottery_type in lottery_types:
        get_lottery_result(lottery_type)
        time.sleep(2)

if __name__ == '__main__':
    main()
