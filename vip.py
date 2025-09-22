# admin/vip.py
from config import OWNER_ID
from app.globals import vips, users, save_json, bot, get_reset_date
from app.logs import log_action
from datetime import datetime, timedelta
from datetime import date

def register(bot):
    @bot.message_handler(commands=['vip'])
    async def vip_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        parts = message.text.split()[1:]
        if len(parts) < 3:
            await bot.reply_to(message, "Usage: /vip {user_id} {days} {remain}")
            return
        try:
            user_id = int(parts[0])
            days = int(parts[1])
            remain = int(parts[2])
            if user_id <= 0:
                await bot.reply_to(message, "Invalid user_id, should be positive.")
                return
        except ValueError:
            await bot.reply_to(message, "Invalid numbers for user_id, days or remain.")
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
                'remains': 2,
                'blocked': False,
                'last_reset': get_reset_date()
            }
        else:
            users[user_id_str]['vip'] = True
        save_json('vips.json', vips)
        save_json('users.json', users)
        await log_action(f"VIP added for user {user_id} for {days} days with daily limit {remain}.")
        await bot.reply_to(message, "VIP added.")

    @bot.message_handler(commands=['premium'])
    async def premium_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        if not vips:
            await bot.reply_to(message, "No VIP users.")
            return
        text = "VIP Users:\n"
        for uid, data in vips.items():
            user = users.get(uid, {})
            text += f"ID: {uid}\nName: {user.get('name', 'Unknown')} @{user.get('username', 'N/A')}\nStart: {data.get('bought_date', 'N/A')}\nExpiry: {data.get('expiry_date', 'N/A')}\nDaily Limit: {data.get('daily_limit', 0)}\nCurrent Remains: {data.get('remains', 0)}\n\n"
        await bot.reply_to(message, text)