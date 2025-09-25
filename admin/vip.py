# admin/vip.py
from typing import Dict, Any
from datetime import datetime, timedelta
from config import OWNER_ID
from app.globals import vips, users, save_json, bot, get_reset_date
from app.logs import log_action

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"
MAX_MSG_LEN = 4000  # Telegram safe message length limit

# Bot attribution text (aligned with grant.py)
BOT_BY_TEXT = '[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n'

# Usage help text
USAGE_TEXT = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐕𝐈𝐏 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐇𝐞𝐥𝐩</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐚𝐠𝐞 ➳ <code>/vip &lt;user_id&gt; &lt;days&gt; &lt;remain&gt;</code>
<a href="{LINK}">[⸙]</a> 𝐄𝐱𝐚𝐦𝐩𝐥𝐞 ➳ <code>/vip 123456789 30 50</code>
<a href="{LINK}">[⸙]</a> 𝐃𝐞𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 ➳ Adds or updates VIP status for a user.
{BOT_BY_TEXT}
"""

def register(bot):
    """Register VIP-related command handlers for the bot."""

    @bot.message_handler(commands=['vip'])
    async def vip_handler(message):
        """
        Handle /vip command to add or update VIP status for a user.
        Only accessible to the bot owner.
        """
        if message.from_user.id != OWNER_ID:
            await bot.reply_to(message, "❌ Unauthorized access. Owner only.", parse_mode="HTML")
            return

        parts = message.text.split(maxsplit=3)[1:]  # Safer split with maxsplit
        if len(parts) < 3:
            await bot.reply_to(message, USAGE_TEXT, parse_mode="HTML", disable_web_page_preview=True)
            return

        try:
            user_id = int(parts[0])
            days = int(parts[1])
            remain = int(parts[2])

            # Validate inputs
            if user_id <= 0:
                await bot.reply_to(message, "❌ User ID must be positive.", parse_mode="HTML")
                return
            if days <= 0:
                await bot.reply_to(message, "❌ Days must be positive.", parse_mode="HTML")
                return
            if remain < 0:
                await bot.reply_to(message, "❌ Remaining requests must be non-negative.", parse_mode="HTML")
                return
        except ValueError:
            await bot.reply_to(message, "❌ Invalid format for user_id, days, or remain.", parse_mode="HTML")
            return

        # Verify user exists
        try:
            user = await bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else "N/A"
            name = user.first_name or "Unknown"
        except Exception as e:
            await bot.reply_to(message, f"❌ Invalid user ID or bot cannot access user: {str(e)}", parse_mode="HTML")
            return

        start = datetime.now()
        expiry = start + timedelta(days=days)
        user_id_str = str(user_id)

        try:
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
                    'username': user.username or '',
                    'name': name,
                    'vip': True,
                    'remains': remain,
                    'blocked': False,
                    'last_reset': get_reset_date()
                }
            else:
                users[user_id_str].update({
                    'username': user.username or '',
                    'name': name,
                    'vip': True,
                    'remains': remain
                })

            save_json("vips.json", vips)
            save_json("users.json", users)
            await log_action(f"VIP added for user {user_id} ({name}, {username}) for {days} days with daily limit {remain} by owner {message.from_user.id}")
        except Exception as e:
            await bot.reply_to(message, f"❌ Failed to save VIP data: {str(e)}", parse_mode="HTML")
            return

        reply_text = f"""
<a href='{LINK}'>┏━━━━━━━⍟</a>
<a href='{LINK}'>┃ ✅ 𝐕𝐈𝐏 𝐀𝐝𝐝𝐞𝐝</a>
<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>

<a href='{LINK}'>[⸙]</a> 𝐔𝐬𝐞𝐫 ➳ <b>{name}</b> ({username})
<a href='{LINK}'>[⸙]</a> 𝐈𝐃 ➳ <code>{user_id}</code>
<a href='{LINK}'>[⸙]</a> 𝐒𝐭𝐚𝐫𝐭 ➳ <b>{start.strftime('%Y-%m-%d %H:%M:%S')}</b>
<a href='{LINK}'>[⸙]</a> 𝐄𝐱𝐩𝐢𝐫𝐲 ➳ <b>{expiry.strftime('%Y-%m-%d %H:%M:%S')}</b>
<a href='{LINK}'>[⸙]</a> 𝐋𝐢𝐦𝐢𝐭 ➳ <b>{remain}</b>
{BOT_BY_TEXT}
"""
        await bot.reply_to(message, reply_text, parse_mode='HTML', disable_web_page_preview=True)

    @bot.message_handler(commands=['premium'])
    async def premium_handler(message):
        """
        Handle /premium command to list all VIP users.
        Only accessible to the bot owner.
        """
        if message.from_user.id != OWNER_ID:
            await bot.reply_to(message, "❌ Unauthorized access. Owner only.", parse_mode="HTML")
            return

        if not vips:
            await bot.reply_to(
                message,
                f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
                f"<a href='{LINK}'>┃ 𝐍𝐨 𝐕𝐈𝐏𝐬 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞</a>\n"
                f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n{BOT_BY_TEXT}",
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            return

        lines = [
            f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
            f"<a href='{LINK}'>┃ 𝐕𝐈𝐏 𝐔𝐬𝐞𝐫𝐬 𝐋𝐢𝐬𝐭</a>\n"
            f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n"
        ]

        for uid, data in vips.items():
            user = users.get(uid, {})
            name = user.get("name", "Unknown")
            username = f"@{user.get('username')}" if user.get("username") else "N/A"
            start = data.get("bought_date", "N/A")
            expiry = data.get("expiry_date", "N/A")
            limit = data.get("daily_limit", 0)
            remains = data.get("remains", 0)

            line = (
                f"<a href='{LINK}'>[⸙]</a> <b>{name}</b> ({username})\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐈𝐃: <code>{uid}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐒𝐭𝐚𝐫𝐭: <code>{start}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐄𝐱𝐩𝐢𝐫𝐲: <code>{expiry}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐋𝐢𝐦𝐢𝐭: <b>{limit}</b>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐑𝐞𝐦𝐚𝐢𝐧𝐬: <b>{remains}</b>\n{BOT_BY_TEXT}\n"
            )
            lines.append(line)

        # Split messages efficiently while respecting MAX_MSG_LEN
        current_message = ""
        for line in lines:
            if len(current_message) + len(line) > MAX_MSG_LEN:
                await bot.reply_to(message, current_message, parse_mode='HTML', disable_web_page_preview=True)
                current_message = line
            else:
                current_message += line

        # Send any remaining text
        if current_message:
            await bot.reply_to(message, current_message, parse_mode='HTML', disable_web_page_preview=True)