# config.py
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID', '0'))
LOGS_GROUP_ID = int(os.getenv('LOGS_GROUP_ID', '0'))
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip().isdigit()]
API_URL = os.getenv('API_URL', 'https://free-like-api-aditya-ffm.vercel.app/like')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'your_username/telegram-bot-data')