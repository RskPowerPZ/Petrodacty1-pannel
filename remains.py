# admin/remains.py
from config import OWNER_ID
from app.globals import grants, save_json, bot, get_reset_date
from app.logs import log_action

def register(bot):
    @bot.message_handler(commands=['setremain'])
    async def remains_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        parts = message.text.split()[1:]
        if len(parts) < 2:
            await bot.reply_to(message, "Usage: /setremain {group_id} {new_remain}")
            return
        try:
            group_id = int(parts[0])
            new_remain = int(parts[1])
            if group_id >= 0:
                await bot.reply_to(message, "Invalid group_id, should be negative.")
                return
        except ValueError:
            await bot.reply_to(message, "Invalid numbers for group_id or new_remain.")
            return
        group_id_str = str(group_id)
        if group_id_str in grants:
            grants[group_id_str]['initial_remain'] = new_remain
            grants[group_id_str]['remain'] = new_remain
            grants[group_id_str]['last_reset'] = get_reset_date()
            save_json('grants.json', grants)
            await log_action(f"Remain for group {group_id} set to {new_remain}")
            await bot.reply_to(message, "Remain updated.")
        else:
            await bot.reply_to(message, "Group not found.")