import requests
from bs4 import BeautifulSoup
import re
import time

def fetch_latest_result():
    url = "https://akjw09d.48489aaa.com:8800/histroy.do?lotCode=LHC&stamp=1729305788117"
    print(f"Fetching data from URL: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            print(f"Response status code: {response.status_code}")
            
            if "chaofancookie" in response.text:
                print("Detected anti-scraping mechanism. Waiting before retry...")
                time.sleep(5)  # Wait for 5 seconds before retrying
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different selectors to find the latest result
            latest_result = soup.find('tr', class_='historyTr') or \
                            soup.find('tr', class_='lhc-history-tr') or \
                            (soup.find('table', class_='lhc-history-table') and soup.find('table', class_='lhc-history-table').find('tr'))
            
            if latest_result:
                print("Found latest result:", latest_result)
                cells = latest_result.find_all('td')
                if len(cells) >= 4:
                    period = cells[0].text.strip()
                    numbers = ' '.join([span.text for span in cells[1].find_all('span', class_='ball')])
                    special = cells[2].find('span', class_='ball').text
                    zodiac = cells[3].find('span', class_='zodiac-3d').get('title')
                    result = f"第{period}期：{numbers}特码 {special} {zodiac}"
                    print(f"Latest result: {result}")
                    return result
            
            print("Failed to find latest result. Page content:")
            print(soup.prettify())
            return None
        
        except Exception as e:
            print(f"Error occurred: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying... (Attempt {attempt + 2} of {max_retries})")
                time.sleep(5)
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
