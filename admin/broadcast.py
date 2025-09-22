# admin/broadcast.py
from config import OWNER_ID
from app.globals import users, grants, bot
from app.logs import log_action

def register(bot):
    @bot.message_handler(commands=['broad'])
    async def broadcast_handler(message):
        if message.from_user.id != OWNER_ID:
            return
        if not message.reply_to_message:
            await bot.reply_to(message, "Reply to a message to broadcast.")
            return
        broadcast_msg = message.reply_to_message
        sent_count = 0
        for uid in list(users.keys()):
            try:
                await bot.copy_message(int(uid), message.chat.id, broadcast_msg.message_id)
                sent_count += 1
            except:
                pass
        for gid in list(grants.keys()):
            try:
                await bot.copy_message(int(gid), message.chat.id, broadcast_msg.message_id)
                sent_count += 1
            except:
                pass
        await log_action(f"Broadcast sent to {sent_count} chats/users.")
        await bot.reply_to(message, f"Broadcast sent to {sent_count} recipients.")