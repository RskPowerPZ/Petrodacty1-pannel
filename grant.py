# admin/grant.py
from config import OWNER_ID
from app.globals import grants, save_json, bot, get_reset_date
from app.logs import log_action
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"
MAX_MSG_LEN = 4000  # Telegram safe limit

def register(bot):
    @bot.message_handler(commands=['grant'])
    async def grant_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        parts = message.text.split()[1:]
        if len(parts) < 2:
            await bot.reply_to(message,
                f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n<a href='{LINK}'>┃ ᴜsᴀɢᴇ</a>\n<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\nᴜsᴀɢᴇ: /grant &lt;ɢʀᴏᴜᴘ_ɪᴅ&gt; &lt;ʀᴇᴍᴀɪɴɪɴɢ_ʀᴇǫᴜᴇsᴛs&gt;",
                parse_mode='HTML'
            )
            return

        try:
            group_id = int(parts[0])
            remain = int(parts[1])
            if group_id >= 0:
                await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ɢʀᴏᴜᴘ_ɪᴅ, sʜᴏᴜʟᴅ ʙᴇ ɴᴇɢᴀᴛɪᴠᴇ.")
                return
        except ValueError:
            await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀs ғᴏʀ ɢʀᴏᴜᴘ_ɪᴅ ᴏʀ ʀᴇᴍᴀɪɴ.")
            return

        try:
            chat = await bot.get_chat(group_id)
            group_name = chat.title or 'ᴜɴɴᴀᴍᴇᴅ'
        except:
            await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ɢʀᴏᴜᴘ_ɪᴅ ᴏʀ ʙᴏᴛ ɴᴏᴛ ɪɴ ɢʀᴏᴜᴘ.")
            return

        group_id_str = str(group_id)
        grants[group_id_str] = {
            'name': group_name,
            'initial_remain': remain,
            'remain': remain,
            'promotion_channel': None,
            'approved': False,
            'last_reset': get_reset_date()
        }
        save_json('grants.json', grants)
        await log_action(f"ɢʀᴀɴᴛ ᴀᴅᴅᴇᴅ ғᴏʀ ɢʀᴏᴜᴘ {group_id} ᴡɪᴛʜ {remain} ʀᴇᴍᴀɪɴs.")

        await bot.reply_to(message,
            f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n<a href='{LINK}'>┃ ✅ ɢʀᴀɴᴛ ᴀᴅᴅᴇᴅ</a>\n<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\n<a href='{LINK}'>ɢʀᴏᴜᴘ:</a> <b>{group_name}</b>\n<a href='{LINK}'>ʀᴇᴍᴀɪɴs:</a> <b>{remain}</b>\n<a href='{LINK}'>ʙᴏᴛ ʙʏ ➳</a> <a href='{LINK}'>꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>",
            parse_mode='HTML'
        )

    @bot.message_handler(commands=['grants'])
    async def grants_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        if not grants:
            await bot.reply_to(message,
                f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n<a href='{LINK}'>┃ ɴᴏ ɢʀᴀɴᴛs ᴀᴠᴀɪʟᴀʙʟᴇ</a>\n<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>",
                parse_mode='HTML'
            )
            return

        lines = [f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n<a href='{LINK}'>┃ ɢʀᴀɴᴛs ʟɪsᴛ</a>\n<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n"]
        for gid, data in grants.items():
            name = data.get('name', 'ᴜɴɴᴀᴍᴇᴅ')
            remain = data.get('remain', 0)
            link = data.get('promotion_channel') or "ɴ/ᴀ"
            line = f"<a href='{LINK}'>[⸙]</a> <b>{name}</b>\n<a href='{LINK}'>ɪᴅ:</a> <code>{gid}</code> | <a href='{LINK}'>ʀᴇᴍᴀɪɴs:</a> <b>{remain}</b> | <a href='{LINK}'>ɪɴᴠɪᴛᴇ:</a> {link}\n"
            lines.append(line)

        full_text = ''.join(lines)

        # Split message if too long
        for i in range(0, len(full_text), MAX_MSG_LEN):
            await bot.reply_to(message, full_text[i:i+MAX_MSG_LEN], parse_mode='HTML', disable_web_page_preview=True)