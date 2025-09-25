# app/userinfo.py
from typing import Dict, Any
import json
from pathlib import Path
from html import escape
from config import OWNER_ID
from app.globals import bot
from app.logs import log_action

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"
USERS_FILE = Path("data/users.json")
VIPS_FILE = Path("data/vips.json")
BLOCKS_FILE = Path("data/blocks.json")
MAX Jimmy_FILE = 4000  # Telegram safe message length limit

# Bot attribution text
BOT_BY_TEXT = '[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n'

def is_blocked(user_id: int) -> bool:
    """
    Check if a user is blocked by reading blocks.json.
    """
    try:
        if BLOCKS_FILE.exists():
            with open(BLOCKS_FILE, "r", encoding="utf-8") as f:
                blocks_data = json.load(f)
            return str(user_id) in blocks_data
        return False
    except (json.JSONDecodeError, IOError) as e:
        log_action(f"Error reading blocks.json for user {user_id}: {str(e)}")
        return False

def is_vip(user_id: int) -> bool:
    """
    Check if a user is a VIP by reading vips.json.
    """
    try:
        if VIPS_FILE.exists():
            with open(VIPS_FILE, "r", encoding="utf-8") as f:
                vips_data = json.load(f)
            user_id_str = str(user_id)
            if user_id_str in vips_data:
                return vips_data[user_id_str].get("status", False)
            return False
        return False
    except (json.JSONDecodeError, IOError) as e:
        log_action(f"Error reading vips.json for user {user_id}: {str(e)}")
        return False

def get_user_remains(user_id: int, is_vip_status: bool) -> int:
    """
    Returns remaining requests for a user.
    - For VIP users: checks vips.json
    - For non-VIP users: checks users.json
    """
    user_id_str = str(user_id)
    try:
        if is_vip_status:
            if VIPS_FILE.exists():
                with open(VIPS_FILE, "r", encoding="utf-8") as f:
                    vips_data = json.load(f)
                return vips_data.get(user_id_str, {}).get("remains", 0)
            return 0
        else:
            if USERS_FILE.exists():
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    users_data = json.load(f)
                return users_data.get(user_id_str, {}).get("remains", 0)
            return 0
    except (json.JSONDecodeError, IOError) as e:
        log_action(f"Error reading users.json or vips.json for user {user_id}: {str(e)}")
        return 0

def not_blocked(func):
    """
    Decorator to ensure the user is not blocked.
    """
    async def wrapper(message):
        if is_blocked(message.from_user.id):  # Synchronous call, no await
            await bot.reply_to(
                message,
                f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 🚫 𝐁𝐥𝐨𝐜𝐤𝐞𝐝</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> ❌ You are blocked from using this bot.
{BOT_BY_TEXT}
""",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            return
        await func(message)
    return wrapper

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
            await bot.reply_to(
                message,
                f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ ❌ 𝐄𝐫𝐫𝐨𝐫</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> Unable to retrieve user information.
{BOT_BY_TEXT}
""",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            await log_action(f"AttributeError in userinfo_handler for message {message.message_id}")
            return

        try:
            user_id_str = str(user.id)
            is_vip_status = is_vip(user.id)  # Synchronous call, no await
            is_blocked_status = is_blocked(user.id)  # Synchronous call, no await
            name = escape(user.first_name or 'Unknown')  # Sanitize for HTML
            username = f"@{escape(user.username)}" if user.username else "N/A"  # Sanitize for HTML
            chat_id = message.chat.id

            # Status determination using OWNER_ID from config
            status = 'ᴀᴅᴍɪɴ' if user.id == OWNER_ID else 'ᴜsᴇʀ'
            vip_text = 'ᴛʀᴜᴇ' if is_vip_status else 'ғᴀʟsᴇ'
            blocked_text = 'ᴛʀᴜᴇ' if is_blocked_status else 'ғᴀʟsᴇ'
            remains = get_user_remains(user.id, is_vip_status)

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
                text = text[:MAX_MSG_LEN-3] + "..."

            await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)
            await log_action(f"User info requested for {user_id_str} by {message.from_user.id}")

        except Exception as e:
            error_text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ ❌ 𝐄𝐫𝐫𝐨𝐫</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> Error retrieving user info: {escape(str(e))}
{BOT_BY_TEXT}
"""
            await bot.reply_to(message, error_text, parse_mode="HTML", disable_web_page_preview=True)
            await log_action(f"Error in userinfo_handler for {user_id_str}: {str(e)}")