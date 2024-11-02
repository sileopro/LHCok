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
            
            # 根据彩种类型查找对应区域
            lottery_names = {
                'lam': '老澳门六合彩',
                'xam': '新澳门六合彩',
                'hk': '六合彩'
            }
            
            # 查找开奖结果
            lottery_sections = soup.find_all('div', class_='lottery-section')
            for section in lottery_sections:
                title = section.find('div', class_='lottery-title')
                if title and lottery_names[lottery_type] in title.text:
                    # 获取期数
                    period = section.find('div', text=lambda t: t and '第' in t and '开奖结果' in t)
                    period = period.text.split('第')[1].split('开奖结果')[0].strip() if period else '未知'
                    
                    # 获取号码
                    numbers = []
                    number_elements = section.find_all('div', class_=lambda x: x and ('red' in x or 'green' in x or 'blue' in x))
                    for elem in number_elements:
                        if elem.text.strip().isdigit():
                            numbers.append(elem.text.strip())
                    
                    # 获取生肖
                    zodiac_elements = section.find_all('div', text=lambda t: t and any(z in t for z in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']))
                    zodiacs = [elem.text.strip() for elem in zodiac_elements]
                    
                    # 格式化结果
                    result = (
                        f"期数: {period}\n"
                        f"开奖时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"号码: {' '.join(numbers)}\n"
                        f"生肖: {' '.join(zodiacs)}\n"
                    )
                    
                    # 保存结果
                    with open(f'{lottery_type}.txt', 'w', encoding='utf-8') as f:
                        f.write(result)
                    print(f"成功保存 {lottery_type} 开奖结果:\n{result}")
                    break
            else:
                print(f"未找到 {lottery_type} 的开奖信息")
                
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
