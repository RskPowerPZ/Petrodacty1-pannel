# tools/connect.py
from config import OWNER_ID
from app.globals import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def register(bot):
    @bot.message_handler(commands=['connect'])
    async def connect_handler(message):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Tap to See Commands!", callback_data="show_commands"))
        await bot.reply_to(message, "Click the button:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == "show_commands")
    async def show_commands(call):
        if call.from_user.id == OWNER_ID:
            text = "Admin Commands:\n/block\n/unblock\n/blocklist\n/broad\n/grant\n/grants\n/promotion\n/approve\n/vip\n/premium\n/setremain\n/likes"
        else:
            text = "User Commands:\n/like {region} {uid}\n/add {region} {uid}\n/autolist\n/remain\n/id\n/userinfo\n/check\n/connect"
        await bot.edit_message_text(text, call.message.chat.id, call.message.id)