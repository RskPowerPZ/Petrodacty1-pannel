# admin/mode.py
from config import OWNER_ID
from app.globals import grants, save_json, bot
from app.logs import log_action

def register(bot):
    @bot.message_handler(commands=['promotion'])
    async def promotion_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        parts = message.text.split()[1:]
        if len(parts) < 2:
            await bot.reply_to(message, "Usage: /promotion {group_id} {channel_link}")
            return
        try:
            group_id = int(parts[0])
            if group_id >= 0:
                await bot.reply_to(message, "Invalid group_id, should be negative.")
                return
        except ValueError:
            await bot.reply_to(message, "Invalid group_id.")
            return
        channel_link = parts[1]
        group_id_str = str(group_id)
        if group_id_str in grants:
            grants[group_id_str]['promotion_channel'] = channel_link
            save_json('grants.json', grants)
            await log_action(f"Promotion channel set for group {group_id} to {channel_link}")
            await bot.reply_to(message, "Promotion channel set.")
        else:
            await bot.reply_to(message, "Group not granted.")

    @bot.message_handler(commands=['approve'])
    async def approve_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        parts = message.text.split()[1:]
        if not parts:
            await bot.reply_to(message, "Usage: /approve {group_id}")
            return
        try:
            group_id = int(parts[0])
            if group_id >= 0:
                await bot.reply_to(message, "Invalid group_id, should be negative.")
                return
        except ValueError:
            await bot.reply_to(message, "Invalid group_id.")
            return
        group_id_str = str(group_id)
        if group_id_str in grants:
            grants[group_id_str]['approved'] = True
            save_json('grants.json', grants)
            await log_action(f"Group {group_id} approved.")
            await bot.reply_to(message, "Group approved.")
        else:
            await bot.reply_to(message, "Group not found.")