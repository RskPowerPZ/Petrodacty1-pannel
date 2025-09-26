import json
from pathlib import Path
from app.globals import bot
from app.vip import check_vip_status

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"
USERS_FILE = Path("data/users.json")
VIPS_FILE = Path("data/vips.json")
BLOCKS_FILE = Path("data/blocks.json")

BOT_BY_TEXT = '𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>'


def get_user_remains(user_id: int, is_vip: bool) -> int:
    """Remaining requests:
    - VIP → vips.json
    - Normal → users.json
    """
    user_id_str = str(user_id)

    if is_vip:
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


def is_user_blocked(user_id: int) -> bool:
    """Check directly from blocks.json"""
    if BLOCKS_FILE.exists():
        with open(BLOCKS_FILE, "r", encoding="utf-8") as f:
            blocks_data = json.load(f)
        return str(user_id) in blocks_data
    return False


def register(bot):
    @bot.message_handler(commands=['info'])
    async def userinfo_handler(message):
        if message.reply_to_message:
            user = message.reply_to_message.from_user
        else:
            user = message.from_user

        user_id_str = str(user.id)
        is_vip = await check_vip_status(user.id)
        blocked_val = is_user_blocked(user.id)

        # Basic details
        name = user.first_name or 'Unknown'
        username = f"@{user.username}" if user.username else "N/A"
        chat_id = message.chat.id

        # Status
        status = 'ᴀᴅᴍɪɴ' if user.id in [7470004765] else 'ᴜsᴇʀ'
        vip_text = 'ᴛʀᴜᴇ' if is_vip else 'ғᴀʟsᴇ'
        blocked_text = 'ᴛʀᴜᴇ' if blocked_val else 'ғᴀʟsᴇ'

        # Remaining requests
        remains = get_user_remains(user.id, is_vip)

        # Final styled text
        text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐔𝐬𝐞𝐫 𝐈𝐧𝐟ᴏ</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐍𝐚𝐦𝐞 ➳ <b>{name}</b>
<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐞𝐫𝐧ᴀᴍᴇ ➳ <b>{username}</b>
<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐞ʀ 𝐈ᴅ ➳ <code>{user_id_str}</code>
<a href="{LINK}">[⸙]</a> 𝐂ʜᴀᴛ 𝐈ᴅ ➳ <code>{chat_id}</code>
<a href="{LINK}">[⸙]</a> 𝐒ᴛᴀᴛᴜs ➳ <b>{status}</b>
<a href="{LINK}">[⸙]</a> 𝐕ɪᴘ ➳ <b>{vip_text}</b>
<a href="{LINK}">[⸙]</a> 𝐁ʟᴏᴄᴋᴇᴅ ➳ <b>{blocked_text}</b>
<a href="{LINK}">[⸙]</a> 𝐑ᴇᴍᴀɪɴɪɴɢ 𝐑ᴇǫᴜᴇsᴛs ➳ <b>{remains}</b>

{BOT_BY_TEXT}
"""

        await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)