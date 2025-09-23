# app/logs.py
from datetime import datetime
from config import LOGS_GROUP_ID
from app.globals import bot
from github_utils import append_to_logs

async def log_action(message):
    timestamp = datetime.now().strftime('%H:%M %d-%m-%Y')
    log_text = f"[{timestamp}] {message}"
    append_to_logs(log_text)
    if LOGS_GROUP_ID:
        try:
            await bot.send_message(LOGS_GROUP_ID, log_text)
        except:
            pass