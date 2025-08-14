import requests
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def test_discord_webhook(url):
    """測試Discord Webhook是否可用"""
    if not url:
        print("錯誤：未設定 DISCORD_WEBHOOK_URL。請檢查 .env 檔案。")
        return

    test_message = {"content": "這是一條來自測試腳本的訊息。"}
    try:
        response = requests.post(url, json=test_message)
        response.raise_for_status()  # 如果狀態碼不是2xx，則拋出HTTPError
        print(f"Discord Webhook 測試成功！狀態碼：{response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Discord Webhook 測試失敗：{e}")
        print("請檢查您的 Discord Webhook URL 是否正確，或網路連線。")

if __name__ == "__main__":
    test_discord_webhook(DISCORD_WEBHOOK_URL)
