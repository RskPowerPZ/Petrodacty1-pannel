# admin/likes.py
from config import OWNER_ID
from app.globals import bot
from app.logs import log_action

def register(bot):
    @bot.message_handler(commands=['likes'])
    async def likes_admin_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        try:
            with open('data/logs.txt', 'r') as f:
                logs = f.readlines()
            like_logs = [line for line in logs if 'Like executed' in line][-10:]  # Last 10 like actions
            if not like_logs:
                await bot.reply_to(message, "No recent like actions.")
                return
            text = "Recent Like Actions:\n"
            for log in like_logs:
                text += log.strip() + "\n"
            await bot.reply_to(message, text)
        except Exception as e:
            await log_action(f"Error in /likes command: {str(e)}")
            await bot.reply_to(message, "Error retrieving like logs.")