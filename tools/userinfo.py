# app/userinfo.py
from typing import Dict, Any
import json
from pathlib import Path
from html import escape  # For HTML sanitization
from config import OWNER_ID  # Use OWNER_ID from config
from app.block import not_blocked, is_blocked
from app.globals import bot
from app.vip import check_vip_status

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"
USERS_FILE = Path("data/users.json")
VIPS_FILE = Path("data/vips.json")
MAX_MSG_LEN = 4000  # Telegram safe message length limit

# Bot attribution text (aligned with grant.py and vip.py)
BOT_BY_TEXT = '[⸙] 𝐃𝐞𝐯➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n'

def get_user_remains(user_id: int, is_vip: bool) -> int:
    """
    Returns remaining requests for a user.
    - For VIP users: checks vips.json
    - For non-VIP users: checks users.json
    """
    user_id_str = str(user_id)

    if is_vip:
        try:
            if VIPS_FILE.exists():
                with open(VIPS_FILE, "r", encoding="utf-8") as f:
                    vips_data = json.load(f)
                return vips_data.get(user_id_str, {}).get("remains", 0)
            return 0
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading vips.json: {str(e)}")  # Log error for debugging
            return 0
    else:
        try:
            if USERS_FILE.exists():
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    users_data = json.load(f)
                return users_data.get(user_id_str, {}).get("remains", 0)
            return 0
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading users.json: {str(e)}")  # Log error for debugging
            return 0

def register(bot):
    """Register user info command handler for the bot."""

    @bot.message_handler(commands=['info'])
    @not_blocked
    async def userinfo_handler(message):
        """
        Handle /info command to display user information.
        Supports replying to a message to get info about another user.
        """
        try:
            # Determine target user (reply or self)
            user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        except AttributeError:
            await bot.reply_to(message, "❌ Unable to retrieve user information.", parse_mode="HTML")
            return

        try:
            user_id_str = str(user.id)
            is_vip = await check_vip_status(user.id)
            is_blocked_val = await is_blocked(user.id)
            name = escape(user.first_name or 'Unknown')  # Sanitize for HTML
            username = f"@{escape(user.username)}" if user.username else "N/A"  # Sanitize for HTML
            chat_id = message.chat.id

            # Status determination using OWNER_ID from config
            status = 'ᴀᴅᴍɪɴ' if user.id == OWNER_ID else 'ᴜsᴇʀ'
            vip_text = 'ᴛʀᴜᴇ' if is_vip else 'ғᴀʟsᴇ'
            blocked_text = 'ᴛʀᴜᴇ' if is_blocked_val else 'ғᴀʟsᴇ'
            remains = get_user_remains(user.id, is_vip)

            # Ensure response is within MAX_MSG_LEN
            text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐔𝐬𝐞𝐫 𝐈𝐧𝐟𝐨</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐍𝐚𝐦𝐞 ➳ <b>{name}</b>
<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞 ➳ <b>{username}</b>
<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐞𝐫 𝐈𝐃 ➳ <code>{user_id_str}</code>
<a href="{LINK}">[⸙]</a> 𝐂𝐡𝐚𝐭 𝐈𝐃 ➳ <code>{chat_id}</code>
<a href="{LINK}">[⸙]</a> 𝐒𝐭𝐚𝐭𝐮𝐬 ➳ <b>{status}</b>
<a href="{LINK}">[⸙]</a> 𝐕𝐈𝐏 ➳ <b>{vip_text}</b>
<a href="{LINK}">[⸙]</a> 𝐁𝐥𝐨𝐜𝐤𝐞𝐝 ➳ <b>{blocked_text}</b>
<a href="{LINK}">[⸙]</a> 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬 ➳ <b>{remains}</b>
{BOT_BY_TEXT}
"""

            if len(text) > MAX_MSG_LEN:
                text = text[:MAX_MSG_LEN-3] + "..."  # Truncate if too long

            await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)

        except Exception as e:
            await bot.reply_to(message, f"❌ Error retrieving user info: {str(e)}", parse_mode="HTML")
            print(f"Error in userinfo_handler: {str(e)}")  # Log error for debugging