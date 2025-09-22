# main.py
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import BaseMiddleware
from datetime import datetime, timedelta, timezone
import os
import requests

from config import BOT_TOKEN, OWNER_ID, LOGS_GROUP_ID
import app.globals as g
from app.globals import load_json, save_json
from app.logs import log_action
from app.grant import validate_grant, deduct_group_remain, reset_group_if_needed
from app.vip import check_vip_status, deduct_vip_remain
from app.block import is_blocked
from config import API_URL

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Load databases
g.users = load_json('users.json')
g.grants = load_json('grants.json')
g.vips = load_json('vips.json')
g.blocks = load_json('blocks.json')
g.autos = load_json('autos.json')

bot = AsyncTeleBot(BOT_TOKEN)
g.bot = bot

class SaveUserMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_sensitive = False
        self.update_types = ['message']

    async def pre_process(self, message, data):
        if not message.text or not message.text.startswith('/'):
            return
        user_id = str(message.from_user.id)
        if user_id not in g.users:
            g.users[user_id] = {
                'id': user_id,
                'username': message.from_user.username or '',
                'name': message.from_user.first_name or '',
                'vip': False,
                'remains': 2,
                'blocked': False,
                'last_reset': g.get_reset_date()
            }
            save_json('users.json', g.users)
        return

    async def post_process(self, message, data, exception=None):
        pass

bot.setup_middleware(SaveUserMiddleware())

# Import and register handlers from modules
from app.block import not_blocked
from app.response import *
from app.grant import validate_grant, deduct_group_remain
from app.vip import check_vip_status, deduct_vip_remain
from app.mode import check_channel_join

from admin.block import register as register_block
from admin.broadcast import register as register_broadcast
from admin.grant import register as register_grant
from admin.likes import register as register_likes_admin
from admin.mode import register as register_mode
from admin.remains import register as register_remains_admin
from admin.vip import register as register_vip

from tools.connect import register as register_connect
from tools.idinfo import register as register_idinfo
from tools.remain import register as register_remain
from tools.userinfo import register as register_userinfo
from tools.likes import register as register_likes_user, execute_like

# Register all
register_block(bot)
register_broadcast(bot)
register_grant(bot)
register_likes_admin(bot)
register_mode(bot)
register_remains_admin(bot)
register_vip(bot)

register_connect(bot)
register_idinfo(bot)
register_remain(bot)
register_userinfo(bot)
register_likes_user(bot)

async def auto_like_loop():
    while True:
        await asyncio.sleep(3600)  # Check every hour
        ist = timezone(timedelta(hours=5, minutes=30))
        now = datetime.now(ist)
        if now.hour != 4 or now.minute > 5:  # Run only around 4 AM IST
            continue
        for user_id_str, items in list(g.autos.items()):
            user_id = int(user_id_str)
            if await is_blocked(user_id):
                continue
            for item in items:
                last_liked = datetime.fromisoformat(item.get('last_liked', '2000-01-01T00:00:00'))
                if now - last_liked < timedelta(hours=24):
                    continue
                # Find a group where the user can execute the like
                group_id = None
                for gid in g.grants.keys():
                    if await validate_grant(int(gid)):
                        group_id = int(gid)
                        break
                if not group_id:
                    await log_action(f"No valid group for auto like by user {user_id_str}")
                    continue
                is_vip = await check_vip_status(user_id)
                user_data = g.users.get(user_id_str, {})
                if is_vip:
                    if g.vips.get(user_id_str, {}).get('remains', 0) <= 0:
                        continue
                else:
                    current_reset = g.get_reset_date()
                    last_reset = user_data.get('last_reset', '2000-01-01')
                    if last_reset < current_reset:
                        user_data['remains'] = 2
                        user_data['last_reset'] = current_reset
                        g.users[user_id_str] = user_data
                        save_json('users.json', g.users)
                    if user_data.get('remains', 0) <= 0:
                        continue
                error, success_text = await execute_like(item['region'], item['uid'], user_id, group_id, auto=True)
                if error:
                    await log_action(f"Auto like failed for {user_id_str}, {item['region']} {item['uid']}: {error}")
                    continue
                await deduct_group_remain(group_id)
                if is_vip:
                    await deduct_vip_remain(user_id)
                else:
                    user_data['remains'] -= 1
                    g.users[user_id_str] = user_data
                    save_json('users.json', g.users)
                item['last_liked'] = now.isoformat()
                save_json('autos.json', g.autos)
                await log_action(f"Auto like executed for {item['region']} {item['uid']} by user {user_id_str} in group {group_id}")
                try:
                    await bot.send_message(user_id, success_text, parse_mode="HTML", disable_web_page_preview=True)
                except:
                    await log_action(f"Failed to notify user {user_id_str} of auto like")

asyncio.create_task(auto_like_loop())

# Run bot
asyncio.run(bot.infinity_polling(timeout=20, request_timeout=600))