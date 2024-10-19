import requests
from bs4 import BeautifulSoup
import re
import time
import random

def fetch_latest_result():
    url = "https://akjw09d.48489aaa.com:8800/histroy.do?lotCode=LHC&stamp=1729305788117"
    print(f"Fetching data from URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = session.get(url)
            print(f"Response status code: {response.status_code}")
            
            if "chaofancookie" in response.text:
                print(f"Detected anti-scraping mechanism. Waiting before retry... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(random.uniform(30, 60))  # Wait between 30 to 60 seconds
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试找到包含开奖结果的元素
            result_element = soup.find('div', text=re.compile(r'第\s*\d+\s*开奖结果'))
            if result_element:
                period = re.search(r'第\s*(\d+)\s*开奖结果', result_element.text).group(1)
                numbers = []
                zodiac = []
                for sibling in result_element.find_next_siblings():
                    match = re.match(r'(\d+)(\w+)', sibling.text.strip())
                    if match:
                        numbers.append(match.group(1))
                        zodiac.append(match.group(2))
                    if len(numbers) == 7:  # 6个平码 + 1个特码
                        break
                
                if len(numbers) == 7:
                    result = f"第{period}期：{' '.join(numbers[:-1])} 特码 {numbers[-1]} {zodiac[-1]}"
                    print(f"Latest result: {result}")
                    return result
            
            print("Failed to find latest result. Page content:")
            print(soup.prettify())
            return None
        
        except Exception as e:
            print(f"Error occurred: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying... (Attempt {attempt + 2} of {max_retries})")
                time.sleep(random.uniform(30, 60))
            else:
                print("Max retries reached. Unable to fetch data.")
                return None

def update_txt_file(new_result):
    print("Updating 1.txt file")
    try:
        with open('1.txt', 'r+', encoding='utf-8') as file:
            content = file.readlines()
            if content and new_result.split('：')[0] not in content[0]:
                content.insert(0, new_result + '\n')
                file.seek(0)
                file.writelines(content)
                print("File updated with new result:", new_result)
            else:
                print("No update needed. Latest result already present.")
    except Exception as e:
        print(f"Error updating file: {e}")

if __name__ == "__main__":
    print("Starting fetch_latest_result.py")
    latest_result = fetch_latest_result()
    if latest_result:
        update_txt_file(latest_result)
    else:
        print("Failed to fetch latest result.")
    print("fetch_latest_result.py completed")
