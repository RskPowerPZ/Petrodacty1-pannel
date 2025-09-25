# admin/mode.py
from config import OWNER_ID
from app.globals import grants, save_json, bot
from app.logs import log_action
import validators  # Assuming validators is installed for URL validation

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
                await bot.reply_to(message, "Invalid group_id, should be negative for groups.")
                return
        except ValueError:
            await bot.reply_to(message, "Invalid group_id. Must be an integer.")
            return
        channel_link = ' '.join(parts[1:])  # Join in case link has spaces or multiple parts
        if not validators.url(channel_link):
            await bot.reply_to(message, "Invalid channel link. Must be a valid URL.")
            return
        group_id_str = str(group_id)
        if group_id_str in grants:
            grants[group_id_str]['promotion_channel'] = channel_link
            save_json('grants.json', grants)
            await log_action(f"Promotion channel set for group {group_id} to {channel_link}")
            await bot.reply_to(message, f"Promotion channel set to {channel_link} for group {group_id}.")
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
                await bot.reply_to(message, "Invalid group_id, should be negative for groups.")
                return
        except ValueError:
            await bot.reply_to(message, "Invalid group_id. Must be an integer.")
            return
        if len(parts) > 1:
            await bot.reply_to(message, "Warning: Extra arguments ignored.")
        group_id_str = str(group_id)
        if group_id_str in grants:
            grants[group_id_str]['approved'] = True
            save_json('grants.json', grants)
            await log_action(f"Group {group_id} approved.")
            await bot.reply_to(message, f"Group {group_id} approved.")
        else:
            await bot.reply_to(message, "Group not granted.")