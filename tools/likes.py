import requests
from datetime import datetime, date, timedelta
import asyncio
from config import API_URL
from app.response import *
from app.logs import log_action
from app.grant import validate_grant, deduct_group_remain, reset_group_if_needed
from app.vip import check_vip_status, deduct_vip_remain
from app.mode import check_channel_join
from app.block import not_blocked, is_blocked
from app.globals import users, vips, autos, save_json, bot, grants, get_reset_date
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

LINK = "https://t.me/+63yIS-gsxsFiYmU1"

async def execute_like(region, uid, user_id, group_id=None, auto=False):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(f"{API_URL}?region={region}&uid={uid}&key=@adityaapis", headers=headers, timeout=10)
        await log_action(f"API status: {resp.status_code} response: {resp.text}")
        data = resp.json()
        if not data.get('success'):
            error = data.get('error', 'Unknown error')
            if 'maxed' in error.lower():
                return MAXED_OUT, None
            else:
                return f"API Error: {error}", None
        time_str = datetime.now().strftime('%H:%M %d-%m-%Y')
        text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ ✅ {'𝐀𝐮𝐭𝐨 𝐋𝐢𝐤𝐞' if auto else '𝐋𝐢𝐤𝐞'} 𝐒𝐮𝐜𝐜𝐞𝐬𝐬</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> ɴɪᴄᴋɴᴀᴍᴇ ➳ <b>{data['nickname']}</b>\n
<a href="{LINK}">[⸙]</a> ᴜɪᴅ ➳ <code>{uid}</code>\n
<a href="{LINK}">[⸙]</a> ʙᴇғᴏʀᴇ ➳ <b>{data['before']}</b>\n
<a href="{LINK}">[⸙]</a> ᴀғᴛᴇʀ ➳ <b>{data['after']}</b>\n
<a href="{LINK}">[⸙]</a> ɢɪᴠᴇɴ ➳ <b>{data['given']}</b>\n
<a href="{LINK}">[⸙]</a> ᴛɪᴍᴇ ➳ <code>{time_str}</code>\n
[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n
"""
        return None, text
    except Exception as e:
        await log_action(f"API exception for {uid}: {str(e)}")
        return SERVER_BUSY, None

async def auto_like_runner():
    while True:
        now = datetime.now()
        for user_id_str, item_list in autos.copy().items():
            user_id = int(user_id_str)
            is_vip = await check_vip_status(user_id)
            user_id_str = str(user_id)  # redundant but ok
            remains_ok = False
            if is_vip:
                if vips.get(user_id_str, {}).get('remains', 0) > 0:
                    remains_ok = True
            else:
                current_reset = get_reset_date()
                user_data = users.get(user_id_str, {})
                last_reset = user_data.get('last_reset', '2000-01-01')
                if last_reset < current_reset:
                    user_data['remains'] = 2
                    user_data['last_reset'] = current_reset
                    users[user_id_str] = user_data
                    save_json('users.json', users)
                if user_data.get('remains', 0) > 0:
                    remains_ok = True
            if not remains_ok:
                continue
            for item in item_list:
                last_liked = datetime.fromisoformat(item['last_liked'])
                if now - last_liked > timedelta(days=1):  # Daily auto like
                    region = item['region']
                    uid = item['uid']
                    error, success_text = await execute_like(region, uid, user_id, None, auto=True)
                    if error:
                        await log_action(f"Auto like error for {user_id}: {error}")
                        continue
                    # Deduct remains
                    if is_vip:
                        await deduct_vip_remain(user_id)
                    else:
                        users[user_id_str]['remains'] -= 1
                        save_json('users.json', users)
                    # Update last liked
                    item['last_liked'] = now.isoformat()
                    save_json('autos.json', autos)
                    # Send notification to user
                    try:
                        await bot.send_message(user_id, success_text, parse_mode="HTML", disable_web_page_preview=True)
                    except Exception as e:
                        await log_action(f"Failed to send auto like message to {user_id}: {str(e)}")
                    await log_action(f"Auto like executed for {user_id} for {region} {uid}")
        await asyncio.sleep(3600)  # Check every hour

def register(bot):
    @bot.message_handler(commands=['like'])
    @not_blocked
    async def like_handler(message):
        if message.chat.type not in ['group', 'supergroup']:
            await bot.reply_to(message, "This command is for groups only.")
            return

        parts = message.text.split()[1:]
        if len(parts) < 2:
            await bot.reply_to(message, INVALID_INPUT)
            return

        region = parts[0].lower()
        uid = parts[1]

        if region not in ['ind', 'pk', 'sg', 'na', 'eu'] or not uid.isdigit():
            await bot.reply_to(message, INVALID_INPUT)
            return

        user_id = message.from_user.id
        group_id = message.chat.id
        await reset_group_if_needed(group_id)

        is_vip = await check_vip_status(user_id)
        group_id_str = str(group_id)
        approved = grants.get(group_id_str, {}).get('approved', False)

        # Check channel join if not approved and not VIP
        if not is_vip and not approved:
            joined = await check_channel_join(user_id, group_id)
            if not joined:
                promotion_channel = grants.get(group_id_str, {}).get('promotion_channel')
                if promotion_channel:
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("Join Channel", url=promotion_channel))
                    markup.add(InlineKeyboardButton("I have joined", callback_data=f"check_joined_{group_id}"))
                    await bot.reply_to(message, "To use /like, join the channel first.", reply_markup=markup)
                else:
                    await bot.reply_to(message, "Promotion channel not set.")
                return

        # Check group grant
        if not await validate_grant(group_id):
            await bot.reply_to(message, "Group has no remaining requests or not granted.")
            return

        # Check user limit
        user_id_str = str(user_id)
        if is_vip:
            if vips.get(user_id_str, {}).get('remains', 0) <= 0:
                await bot.reply_to(message, "Your VIP remains are exhausted for today.")
                return
        else:
            current_reset = get_reset_date()
            user_data = users.get(user_id_str, {})
            last_reset = user_data.get('last_reset', '2000-01-01')
            if last_reset < current_reset:
                user_data['remains'] = 2
                user_data['last_reset'] = current_reset
                users[user_id_str] = user_data
                save_json('users.json', users)
            if user_data.get('remains', 0) <= 0:
                await bot.reply_to(message, DAILY_LIMIT)
                return

        # Execute like
        error, success_text = await execute_like(region, uid, user_id, group_id)
        if error:
            await bot.reply_to(message, error)
            return

        # Deduct limits
        await deduct_group_remain(group_id)
        if is_vip:
            await deduct_vip_remain(user_id)
        else:
            users[user_id_str]['remains'] -= 1
            save_json('users.json', users)

        await bot.reply_to(message, success_text, parse_mode="HTML", disable_web_page_preview=True)
        await log_action(f"Like executed by {user_id} in {group_id} for {region} {uid}")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('check_joined_'))
    async def check_joined_callback(call):
        group_id = int(call.data.split('_')[2])
        joined = await check_channel_join(call.from_user.id, group_id)
        if joined:
            await bot.edit_message_text("Joined successfully! Now try /like again.", call.message.chat.id, call.message.id)
        else:
            await bot.edit_message_text("Not joined yet. Please join and click again.", call.message.chat.id, call.message.id)

    @bot.message_handler(commands=['check'])
    @not_blocked
    async def check_handler(message):
        user_id_str = str(message.from_user.id)
        is_vip = await check_vip_status(message.from_user.id)

        if not is_vip:
            text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃  𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ᴠɪᴘ ᴍᴇᴍʙᴇʀ.\n
<a href="{LINK}">[⸙]</a> ᴘʟᴇᴀsᴇ ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴠɪᴘ ᴛᴏ ᴜɴʟᴏᴄᴋ ᴛʜɪs ғᴇᴀᴛᴜʀᴇ.\n
[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n
"""
            await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)
            return

        data = vips.get(user_id_str, {})
        status = "𝐀𝐜𝐭𝐢𝐯𝐞" if is_vip else "𝐄𝐱𝐩𝐢ʀ𝐞𝐝"
        bought_date = data.get("bought_date", "N/A")
        expiry_date = data.get("expiry_date", "N/A")
        daily_limit = data.get("daily_limit", 0)
        remains = data.get("remains", 0)

        text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃  𝐕𝐢𝐩 𝐒𝐭𝐚𝐭𝐮𝐬</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> sᴛᴀᴛᴜs ➳ <code>{status}</code>\n
<a href="{LINK}">[⸙]</a> sᴛᴀʀᴛ ➳ <code>{bought_date}</code>\n
<a href="{LINK}">[⸙]</a> ᴇxᴘɪʀʏ ➳ <code>{expiry_date}</code>\n
<a href="{LINK}">[⸙]</a> ᴅᴀɪʟʏ ʟɪᴍɪᴛ ➳ <code>{daily_limit}</code>\n
<a href="{LINK}">[⸙]</a> ʀᴇᴍᴀɪɴs ➳ <code>{remains}</code>\n
[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n
"""
        await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)
        await log_action(f"VIP status checked by user {user_id_str}")

    @bot.message_handler(commands=['add'])
    @not_blocked
    async def add_auto_handler(message):
        parts = message.text.split()[1:]
        if len(parts) < 2:
            await bot.reply_to(message, INVALID_INPUT)
            return
        region = parts[0].lower()
        uid = parts[1]
        if region not in ['ind', 'pk', 'sg', 'na', 'eu'] or not uid.isdigit():
            await bot.reply_to(message, INVALID_INPUT)
            return
        user_id_str = str(message.from_user.id)
        if user_id_str not in autos:
            autos[user_id_str] = []
        autos[user_id_str].append({'region': region, 'uid': uid, 'last_liked': '2000-01-01T00:00:00'})
        save_json('autos.json', autos)
        await bot.reply_to(message, f"Added {region} {uid} to auto like list.")
        await log_action(f"User {user_id_str} added {region} {uid} to auto likes")

    @bot.message_handler(commands=['autolist'])
    @not_blocked
    async def autolist_handler(message):
        user_id_str = str(message.from_user.id)
        if user_id_str not in autos or not autos[user_id_str]:
            await bot.reply_to(message, "No auto likes added.")
            return
        text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃  𝐀𝐮𝐭𝐨 𝐋𝐢𝐤𝐞𝐬 𝐋𝐢𝐬𝐭</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>\n
"""
        for item in autos[user_id_str]:
            text += f"<a href=\"{LINK}\">[⸙]</a> Region: <code>{item['region']}</code>, UID: <code>{item['uid']}</code>, Last liked: <code>{item.get('last_liked', 'Never')}</code>\n"
        text += f"[⸙] 𝐃𝐞𝐯 ➳ <a href=\"tg://user?id=7439897927\">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>"
        await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)
        await log_action(f"User {user_id_str} requested auto likes list")