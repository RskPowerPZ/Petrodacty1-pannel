# app/block.py
from app.globals import users, blocks, bot
from app.response import BLOCKED

async def is_blocked(user_id):
    user_id_str = str(user_id)
    return user_id_str in blocks or users.get(user_id_str, {}).get('blocked', False)

def not_blocked(handler):
    async def wrapper(message):
        if await is_blocked(message.from_user.id):
            await bot.reply_to(message, BLOCKED)
            return
        await handler(message)
    return wrapper