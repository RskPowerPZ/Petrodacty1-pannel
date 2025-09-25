# tools/remain.py
from app.block import not_blocked
from app.globals import users, grants, vips, save_json, bot, get_reset_date
from app.vip import check_vip_status
from app.grant import reset_group_if_needed

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"  # apna channel/group link yaha daalna

def register(bot):
    @bot.message_handler(commands=['remain'])
    @not_blocked
    async def remain_handler(message):
        try:
            user_id = str(message.from_user.id)
            group_id = str(message.chat.id)

            # group reset check
            await reset_group_if_needed(message.chat.id)

            # check VIP status
            is_vip = await check_vip_status(message.from_user.id)
            if is_vip:
                personal = vips.get(user_id, {}).get('remains', 0)
            else:
                current_reset = get_reset_date()
                last_reset = users.get(user_id, {}).get('last_reset', '2000-01-01')

                # reset if needed
                if last_reset < current_reset:
                    users[user_id] = users.get(user_id, {})
                    users[user_id]['remains'] = 2
                    users[user_id]['last_reset'] = current_reset
                    save_json('users.json', users)

                personal = users.get(user_id, {}).get('remains', 0)

            group_remain = grants.get(group_id, {}).get('remain', 0)

            # stylish formatted message
            text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠 𝐫𝐞𝐪𝐮𝐞𝐬𝐭</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐏ᴇʀsᴏɴᴀʟ ʀᴇᴍᴀɪɴs ➳ <b>{personal}</b>
<a href="{LINK}">[⸙]</a> 𝐆ʀᴏᴜᴘ ʀᴇᴍᴀɪɴs ➳ <b>{group_remain}</b>

[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>
"""

            await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)

        except Exception as e:
            await bot.reply_to(message, f"⚠️ Error in remain command: <code>{e}</code>", parse_mode="HTML")