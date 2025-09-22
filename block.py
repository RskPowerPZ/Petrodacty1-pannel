# admin/block.py
from config import OWNER_ID
from app.globals import blocks, users, save_json, bot
from app.block import is_blocked
from app.logs import log_action
from datetime import datetime

def register(bot):
    @bot.message_handler(commands=['block'])
    async def block_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        parts = message.text.split()[1:]
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            reason = ' '.join(parts)
        else:
            if not parts:
                await bot.reply_to(message, "Provide user_id or reply to message.")
                return
            try:
                user_id = int(parts[0])
                if user_id <= 0:
                    await bot.reply_to(message, "Invalid user_id, should be positive.")
                    return
            except ValueError:
                await bot.reply_to(message, "Invalid user_id.")
                return
            reason = ' '.join(parts[1:])
        user_id_str = str(user_id)
        blocks[user_id_str] = {
            'blocked_at': datetime.now().isoformat(),
            'reason': reason
        }
        if user_id_str in users:
            users[user_id_str]['blocked'] = True
            save_json('users.json', users)
        save_json('blocks.json', blocks)
        await log_action(f"User {user_id} blocked. Reason: {reason}")
        await bot.reply_to(message, f"User {user_id} blocked.")

    @bot.message_handler(commands=['unblock'])
    async def unblock_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        parts = message.text.split()[1:]
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            if not parts:
                await bot.reply_to(message, "Provide user_id or reply to message.")
                return
            try:
                user_id = int(parts[0])
                if user_id <= 0:
                    await bot.reply_to(message, "Invalid user_id, should be positive.")
                    return
            except ValueError:
                await bot.reply_to(message, "Invalid user_id.")
                return
        user_id_str = str(user_id)
        if user_id_str in blocks:
            del blocks[user_id_str]
            save_json('blocks.json', blocks)
        if user_id_str in users:
            users[user_id_str]['blocked'] = False
            save_json('users.json', users)
        await log_action(f"User {user_id} unblocked.")
        await bot.reply_to(message, f"User {user_id} unblocked.")

    @bot.message_handler(commands=['blocklist'])
    async def blocklist_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        if not blocks:
            await bot.reply_to(message, "No blocked users.")
            return
        text = "Blocked Users:\n"
        for uid, data in blocks.items():
            user = users.get(uid, {})
            text += f"ID: {uid}\nName: {user.get('name', 'Unknown')}\nUsername: @{user.get('username', 'N/A')}\nBlocked at: {data['blocked_at']}\n\n"
        await bot.reply_to(message, text)