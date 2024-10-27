from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print("请按照以下步骤操作生成会话字符串：")

# 请填入您的API凭证
API_ID = input("输入 API ID: ")
API_HASH = input("输入 API Hash: ")

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("\n您的会话字符串（请复制保存）：")
    print(client.session.save())
