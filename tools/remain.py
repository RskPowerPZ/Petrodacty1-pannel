# tools/remain.py
import json
from pathlib import Path
from app.block import not_blocked
from app.globals import users, grants, vips, save_json, bot, get_reset_date
from app.vip import check_vip_status
from app.grant import reset_group_if_needed

# same BOT_BY_TEXT style as info.py
BOT_BY_TEXT = '𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>'
LINK = "https://t.me/+63yIS-gsxsFiYmU1"
VIPS_FILE = Path("data/vips.json")


def register(bot):
    @bot.message_handler(commands=['remain'])
    @not_blocked
    async def remain_handler(message):
        user_id = message.from_user.id
        user_id_str = str(user_id)
        group_id_str = str(message.chat.id)

        # reset group if needed
        await reset_group_if_needed(message.chat.id)

        # check VIP
        is_vip = await check_vip_status(user_id)

        personal = 0
        if is_vip:
            # load from vips.json
            if VIPS_FILE.exists():
                try:
                    with open(VIPS_FILE, "r", encoding="utf-8") as f:
                        vips_data = json.load(f)
                    entry = vips_data.get(user_id_str) or vips_data.get(int(user_id_str))
                    if entry:
                        personal = int(entry.get("remains", entry.get("daily_limit", 0)))
                except Exception as e:
                    print(f"[remain_handler] Error loading VIP remains: {e}")
        else:
            # normal user remains
            current_reset = get_reset_date()
            last_reset = users.get(user_id_str, {}).get('last_reset', '2000-01-01')
            if last_reset < current_reset:
                users[user_id_str] = {
                    "remains": 2,
                    "last_reset": current_reset
                }
                save_json("users.json", users)
            personal = users.get(user_id_str, {}).get("remains", 0)

        # group remains
        group_remain = grants.get(group_id_str, {}).get("remain", 0)

        # styled output
        text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐏𝐞𝐫𝐬𝐨𝐧𝐚𝐥 ➳ <b>{personal}</b>
<a href="{LINK}">[⸙]</a> 𝐆𝐫𝐨𝐮𝐩 ➳ <b>{group_remain}</b>

{BOT_BY_TEXT}
"""
        await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)