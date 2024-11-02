import requests
import re
import time
from datetime import datetime

def get_page_source():
    """获取页面源码"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    
    try:
        response = requests.get('https://akjw09d.48489aaa.com:8800/', headers=headers, verify=False)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"获取页面源码失败: {str(e)}")
        return None

def extract_lottery_info(html, lottery_name):
    """从HTML中提取开奖信息"""
    try:
        # 使用正则表达式查找包含开奖信息的部分
        pattern = f'{lottery_name}.*?第(\\d+)期.*?开奖结果.*?((?:\\d+[鼠牛虎兔龙蛇马羊猴鸡狗猪]\\s*)+)'
        match = re.search(pattern, html, re.DOTALL)
        
        if match:
            period = match.group(1)
            result_text = match.group(2)
            
            # 提取数字和生肖对
            pairs = re.findall(r'(\d+)([鼠牛虎兔龙蛇马羊猴鸡狗猪])', result_text)
            
            if pairs:
                result = (
                    f"{lottery_name}  第 {period} 开奖结果\n"
                    f"{' '.join([f'{num}{zodiac}' for num, zodiac in pairs])}\n"
                )
                print(f"找到完整结果:\n{result}")
                return result
                
        print(f"未找到 {lottery_name} 的完整开奖信息")
        return None
            
    except Exception as e:
        print(f"提取 {lottery_name} 信息时出错: {str(e)}")
        return None

def main():
    """主函数"""
    lottery_mapping = {
        'lam': '老澳门六合彩',
        'xam': '新澳门六合彩',
        'hk': '六合彩',
        'tc': '台湾六合彩'
    }
    
    try:
        # 获取页面源码
        html = get_page_source()
        if not html:
            print("获取页面源码失败")
            return
            
        # 保存原始HTML用于调试
        with open('debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("已保存原始HTML")
        
        # 获取各彩种结果
        for code, name in lottery_mapping.items():
            print(f"\n正在处理 {name}...")
            result = extract_lottery_info(html, name)
            if result:
                with open(f'{code}.txt', 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"已保存 {name} 开奖结果到 {code}.txt")
            else:
                print(f"未找到 {name} 开奖结果")
                
    except Exception as e:
        print(f"运行出错: {str(e)}")

if __name__ == '__main__':
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
