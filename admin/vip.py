# admin/vip.py
from config import OWNER_ID
from app.globals import vips, users, save_json, bot, get_reset_date
from app.logs import log_action
from datetime import datetime, timedelta

LINK = "https://t.me/+63yIS-gsxsFiYmU1"
MAX_MSG_LEN = 4000  # Telegram safe limit

def register(bot):
    @bot.message_handler(commands=['vip'])
    async def vip_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        parts = message.text.split()[1:]
        if len(parts) < 3:
            await bot.reply_to(
                message,
                f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
                f"<a href='{LINK}'>┃ 𝐔𝐬𝐚𝐠𝐞</a>\n"
                f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\n"
                f"<a href='{LINK}'>/vip &lt;ᴜsᴇʀ_ɪᴅ&gt; &lt;ᴅᴀʏs&gt; &lt;ʀᴇᴍᴀɪɴ&gt;</a>",
                parse_mode="HTML"
            )
            return

        try:
            user_id = int(parts[0])
            days = int(parts[1])
            remain = int(parts[2])
            if user_id <= 0:
                await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ_ɪᴅ, sʜᴏᴜʟᴅ ʙᴇ ᴘᴏsɪᴛɪᴠᴇ.")
                return
        except ValueError:
            await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀs ғᴏʀ ᴜsᴇʀ_ɪᴅ, ᴅᴀʏs ᴏʀ ʀᴇᴍᴀɪɴ.")
            return

        start = datetime.now()
        expiry = start + timedelta(days=days)
        user_id_str = str(user_id)

        vips[user_id_str] = {
            'bought_date': start.isoformat(),
            'expiry_date': expiry.isoformat(),
            'daily_limit': remain,
            'remains': remain,
            'last_reset': get_reset_date()
        }

        if user_id_str not in users:
            users[user_id_str] = {
                'id': user_id_str,
                'username': '',
                'name': '',
                'vip': True,
                'remains': remain,
                'blocked': False,
                'last_reset': get_reset_date()
            }
        else:
            users[user_id_str]['vip'] = True

        save_json("vips.json", vips)
        save_json("users.json", users)

        await log_action(f"VIP added for user {user_id} for {days} days with daily limit {remain}.")

        await bot.reply_to(
            message,
            f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
            f"<a href='{LINK}'>┃ ✅ 𝐕𝐢𝐩 𝐀𝐝𝐝𝐞𝐝</a>\n"
            f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\n"
            f"<a href='{LINK}'>ᴜsᴇʀ:</a> <code>{user_id}</code>\n"
            f"<a href='{LINK}'>sᴛᴀʀᴛ:</a> <b>{start.strftime('%Y-%m-%d %H:%M:%S')}</b>\n"
            f"<a href='{LINK}'>ᴇxᴘɪʀʏ:</a> <b>{expiry.strftime('%Y-%m-%d %H:%M:%S')}</b>\n"
            f"<a href='{LINK}'>ʟɪᴍɪᴛ:</a> <b>{remain}</b>",
            parse_mode="HTML"
        )

    @bot.message_handler(commands=['premium'])
    async def premium_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        if not vips:
            await bot.reply_to(
                message,
                f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
                f"<a href='{LINK}'>┃ 𝐍𝐨 𝐕𝐢𝐩𝐬 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞</a>\n"
                f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>",
                parse_mode="HTML"
            )
            return

        lines = [
            f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
            f"<a href='{LINK}'>┃ 𝐕𝐢𝐩 𝐔𝐬𝐞𝐫𝐬</a>\n"
            f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n"
        ]

        for uid, data in vips.items():
            user = users.get(uid, {})
            name = user.get("name", "ᴜɴᴋɴᴏᴡɴ")
            uname = f"@{user.get('username')}" if user.get("username") else "N/A"
            start = data.get("bought_date", "N/A")
            expiry = data.get("expiry_date", "N/A")
            limit = data.get("daily_limit", 0)
            remains = data.get("remains", 0)

            lines.append(
                f"<a href='{LINK}'>[⸙]</a> <b>{name}</b> {uname}\n"
                f"<a href='{LINK}'>[⸙]</a> ɪᴅ:</a> <code>{uid}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> sᴛᴀʀᴛ:</a> <code>{start}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> ᴇxᴘɪʀʏ:</a> <code>{expiry}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> ʟɪᴍɪᴛ:</a> <b>{limit}</b> | "
                f"<a href='{LINK}'>[⸙]</a> ʀᴇᴍᴀɪɴs:</a> <b>{remains}</b>\n\n"
            )

        full_text = ''.join(lines)

        for i in range(0, len(full_text), MAX_MSG_LEN):
            await bot.reply_to(
                message,
                full_text[i:i+MAX_MSG_LEN],
                parse_mode="HTML",
                disable_web_page_preview=True
            )