from telethon import TelegramClient
import asyncio
import re
import os

# Telegram API credentials
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
session_string = os.environ['SESSION_STRING']

async def fetch_latest_result():
    client = TelegramClient('anon', api_id, api_hash)
    await client.start(session_string)
    
    try:
        # 直接使用频道名称
        messages = await client.get_messages('香港六合彩開獎', limit=5)
        
        for msg in messages:
            if not msg.text:
                continue
                
            # 匹配开奖信息，格式更宽松
            numbers = []
            special = None
            period = None
            
            # 提取期数
            period_match = re.search(r'当前期数：第(\d+)期', msg.text)
            if period_match:
                period = period_match.group(1)
            
            # 提取号码
            number_match = re.findall(r'\d+', msg.text)
            if len(number_match) >= 7:  # 确保至少有6个号码+特码
                numbers = number_match[:6]
                special = number_match[6]
            
            if numbers and special and period:
                formatted_text = f"第{period}期：{' '.join(numbers)} 特码 {special}"
                # 写入文件
                with open('hk.txt', 'a', encoding='utf-8') as f:
                    f.write(formatted_text + '\n')
                # 找到有效数据后退出
                break
                
    except Exception as e:
        print(f"获取数据时出错: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(fetch_latest_result())
