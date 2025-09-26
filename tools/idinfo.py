# tools/idinfo.py
from app.block import not_blocked
from app.globals import bot

LINK = "https://t.me/+63yIS-gsxsFiYmU1"  # apna link yaha daalna

def register(bot):
    @bot.message_handler(commands=['id'])
    @not_blocked
    async def id_handler(message):
        try:
            group_id = message.chat.id
            message_id = message.message_id
            user_id = message.from_user.id
            replied_id = None

            if message.reply_to_message:
                replied_id = message.reply_to_message.from_user.id

            # Stylish formatted text
            text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐈𝐃 𝐈𝐧𝐟𝐨</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐆ʀᴏᴜᴘ ɪᴅ ➳ <code>{group_id}</code>
<a href="{LINK}">[⸙]</a> 𝐌ᴇssᴀɢᴇ ɪᴅ ➳ <code>{message_id}</code>
<a href="{LINK}">[⸙]</a> 𝐔sᴇʀ ɪᴅ ➳ <code>{user_id}</code>
"""

            if replied_id:
                text += f'<a href="{LINK}">[⸙]</a> 𝐑ᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ ➳ <code>{replied_id}</code>\n'

            # Dev credit at bottom
            text += f"""
[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>
"""

            await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)

        except Exception as e:
            await bot.reply_to(message, f"⚠️ Error in id command: <code>{e}</code>", parse_mode="HTML")