
import json
from pathlib import Path
from app.block import not_blocked, is_blocked
from app.globals import bot
from app.vip import check_vip_status

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"
USERS_FILE = Path("data/users.json")
VIPS_FILE = Path("data/vips.json")

def get_user_remains(user_id: int, is_vip: bool) -> int:
"""
Returns remaining requests.
- For VIP users → check vips.json
- For non-VIP users → check users.json
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

def register(bot):
@bot.message_handler(commands=['info'])
@not_blocked
async def userinfo_handler(message):
if message.reply_to_message:
user = message.reply_to_message.from_user
else:
user = message.from_user

user_id_str = str(user.id)  
    is_vip = await check_vip_status(user.id)  
    is_blocked_val = await is_blocked(user.id)  
    name = user.first_name or 'Unknown'  
    username = f"@{user.username}" if user.username else "N/A"  
    chat_id = message.chat.id  

    # Status small caps  
    status = 'ᴀᴅᴍɪɴ' if user.id in [7470004765] else 'usᴇʀ'  
    vip_text = 'ᴛʀᴜᴇ' if is_vip else 'ғᴀʟsᴇ'  
    blocked_text = 'ᴛʀᴜᴇ' if is_blocked_val else 'ғᴀʟsᴇ'  

    # Remaining requests (VIP → vips.json, Normal → users.json)  
    remains = get_user_remains(user.id, is_vip)  

    # HTML text with clickable links on signs  
    text = f"""

<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐔𝐬𝐞𝐫 𝐈𝐧𝐟ᴏ</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> ɴᴀᴍᴇ ➳ <b>{name}</b>\n
<a href="{LINK}">[⸙]</a> ᴜsᴇʀɴᴀᴍᴇ ➳ <b>{username}</b>\n
<a href="{LINK}">[⸙]</a> ᴜsᴇʀ ɪᴅ ➳ <code>{user_id_str}</code>\n
<a href="{LINK}">[⸙]</a> ᴄʜᴀᴛ ɪᴅ ➳ <code>{chat_id}</code>\n\n
<a href="{LINK}">[⸙]</a> sᴛᴀᴛᴜs ➳ {status}\n
<a href="{LINK}">[⸙]</a> Vɪᴘ ➳ {vip_text}\n
<a href="{LINK}">[⸙]</a> Bʟᴏᴄᴋᴇᴅ ➳ {blocked_text}\n
<a href="{LINK}">[⸙]</a> Rᴇᴍᴀɪɴɪɴɢ ʀᴇǫᴜᴇsᴛ ➳ {remains}\n
[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n
"""

await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)

