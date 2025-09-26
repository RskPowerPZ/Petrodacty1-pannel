# admin/likes.py
from config import OWNER_ID
from app.globals import bot
from app.logs import log_action

LINK = "https://t.me/+63yIS-gsxsFiYmU1"

def register(bot):
    @bot.message_handler(commands=['likes'])
    async def likes_admin_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        try:
            with open('data/logs.txt', 'r') as f:
                logs = f.readlines()

            # Filter like logs & show last 10
            like_logs = [line for line in logs if 'Like executed' in line][-10:]

            if not like_logs:
                text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐋𝐢𝐤𝐞𝐬 𝐋𝐨𝐠𝐬</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> ❌ No recent like actions found!
"""
                await bot.reply_to(message, text, parse_mode="HTML")
                return

            # Build stylish log response
            text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐑𝐞𝐜𝐞𝐧𝐭 𝐋𝐢𝐤𝐞𝐬 (𝐋𝐚𝐬𝐭 𝟏𝟎)</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>
"""

            for i, log in enumerate(like_logs, 1):
                text += f'<a href="{LINK}">[⸙]</a> {i}. <code>{log.strip()}</code>\n'

            await bot.reply_to(message, text, parse_mode="HTML")

        except Exception as e:
            error_text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ ⚠️ 𝐄𝐫𝐫𝐨𝐫</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> {str(e)}
"""
            await log_action(f"Error in /likes command: {str(e)}")
            await bot.reply_to(message, error_text, parse_mode="HTML")