# tools/idinfo.py
from app.block import not_blocked
from app.globals import bot

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"

def register(bot):
    @bot.message_handler(commands=['id'])
    @not_blocked
    async def id_handler(message):
        group_id = message.chat.id
        message_id = message.message_id
        user_id = message.from_user.id

        replied_id = None
        if message.reply_to_message:
            replied_id = message.reply_to_message.from_user.id

        text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐈𝐃 𝐈𝐧𝐟𝐨</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> ɢʀᴏᴜᴘ ɪᴅ ➳ <code>{group_id}</code>\n
<a href="{LINK}">[⸙]</a> ᴍᴇssᴀɢᴇ ɪᴅ ➳ <code>{message_id}</code>\n
<a href="{LINK}">[⸙]</a> ᴜsᴇʀ ɪᴅ ➳ <code>{user_id}</code>\n
"""

        if replied_id:
            text += f'<a href="{LINK}">[⸙]</a> ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ ➳ <code>{replied_id}</code>\n'

        await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)