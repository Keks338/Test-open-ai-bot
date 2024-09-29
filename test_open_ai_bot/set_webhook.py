import requests
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
URL = 'https://8e5a-37-99-19-67.ngrok-free.app'
WEBHOOK_URL = f"{URL}/webhook/"

def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    response = requests.get(url)
    print(response.json())

if __name__ == '__main__':
    set_webhook()