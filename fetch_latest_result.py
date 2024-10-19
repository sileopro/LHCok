import requests
from bs4 import BeautifulSoup
import re

def fetch_latest_result():
    url = "https://akjw09d.48489aaa.com:8800/histroy.do?lotCode=LHC&stamp=1729305788117"
    print(f"Fetching data from URL: {url}")
    response = requests.get(url)
    print(f"Response status code: {response.status_code}")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 找到最新的开奖结果
    latest_result = soup.find('tr', class_='historyTr')
    if latest_result:
        cells = latest_result.find_all('td')
        if len(cells) >= 4:
            period = cells[0].text.strip()
            numbers = ' '.join([span.text for span in cells[1].find_all('span', class_='ball')])
            special = cells[2].find('span', class_='ball').text
            zodiac = cells[3].find('span', class_='zodiac-3d').get('title')
            result = f"第{period}期：{numbers}特码 {special} {zodiac}"
            print(f"Latest result: {result}")
            return result
    print("Failed to find latest result")
    return None

def update_txt_file(new_result):
    print("Updating 1.txt file")
    with open('1.txt', 'r+', encoding='utf-8') as file:
        content = file.readlines()
        if content and new_result.split('：')[0] not in content[0]:
            content.insert(0, new_result + '\n')
            file.seek(0)
            file.writelines(content)
            print("File updated with new result:", new_result)
        else:
            print("No update needed. Latest result already present.")

if __name__ == "__main__":
    print("Starting fetch_latest_result.py")
    latest_result = fetch_latest_result()
    if latest_result:
        update_txt_file(latest_result)
    else:
        print("Failed to fetch latest result.")
    print("fetch_latest_result.py completed")
