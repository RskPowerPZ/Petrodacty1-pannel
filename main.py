import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from telebot.async_telebot import AsyncTeleBot
from telebot import BaseMiddleware
from aiohttp import web
import sys
from typing import Dict, Any

from config import BOT_TOKEN
import app.globals as g
from app.globals import load_json, save_json, get_reset_date
from app.logs import log_action
from app.grant import validate_grant, deduct_group_remain
from app.vip import check_vip_status, deduct_vip_remain
from app.block import is_blocked

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize databases with error handling
try:
    g.users = load_json('users.json')
    g.grants = load_json('grants.json')
    g.vips = load_json('vips.json')
    g.blocks = load_json('blocks.json')
    g.autos = load_json('autos.json')
except Exception as e:
    logger.error(f"Failed to load JSON databases: {e}")
    g.users = g.grants = g.vips = g.blocks = g.autos = {}
    save_json('users.json', g.users)
    save_json('grants.json', g.grants)
    save_json('vips.json', g.vips)
    save_json('blocks.json', g.blocks)
    save_json('autos.json', g.autos)

bot = AsyncTeleBot(BOT_TOKEN)
g.bot = bot

# ---------------- MIDDLEWARE ----------------
class SaveUserMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_sensitive = False
        self.update_types = ['message']

    async def pre_process(self, message, data):
        try:
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
                    'last_reset': get_reset_date().isoformat()
                }
                await save_json_async('users.json', g.users)
                logger.info(f"New user registered: {user_id}")
        except Exception as e:
            logger.error(f"Error in SaveUserMiddleware pre_process: {e}")

    async def post_process(self, message, data, exception=None):
        if exception:
            logger.error(f"Middleware processing error: {exception}")

bot.setup_middleware(SaveUserMiddleware())

# ---------------- IMPORT HANDLERS ----------------
try:
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
except ImportError as e:
    logger.error(f"Failed to import handlers: {e}")
    raise

# Register all handlers
for handler in [
    register_block, register_broadcast, register_grant, register_likes_admin,
    register_mode, register_remains_admin, register_vip, register_connect,
    register_idinfo, register_remain, register_userinfo, register_likes_user
]:
    try:
        handler(bot)
    except Exception as e:
        logger.error(f"Failed to register handler {handler.__name__}: {e}")

# ---------------- HTTP SERVER ----------------
async def health_check(request):
    return web.json_response({
        'status': 'running',
        'users_count': len(g.users),
        'autos_count': len(g.autos),
        'timestamp': datetime.now(timezone.utc).isoformat()
    })

async def start_http_server():
    app = web.Application()
    app.add_routes([web.get('/health', health_check)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 5000)
    await site.start()
    logger.info("HTTP server started on http://127.0.0.1:5000")

# ---------------- AUTO LIKE LOOP ----------------
async def auto_like_loop():
    while True:
        try:
            await asyncio.sleep(3600)  # Check every hour
            ist = timezone(timedelta(hours=5, minutes=30))
            now = datetime.now(ist)
            if now.hour != 4 or now.minute > 5:
                continue

            logger.info("Starting auto-like cycle")
            for user_id_str, items in list(g.autos.items()):
                user_id = int(user_id_str)
                if await is_blocked(user_id):
                    logger.info(f"Skipping blocked user: {user_id}")
                    continue

                for item in items:
                    try:
                        last_liked = datetime.fromisoformat(item.get('last_liked', '2000-01-01T00:00:00+00:00'))
                        if now - last_liked < timedelta(hours=24):
                            continue

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
                            current_reset = get_reset_date()
                            last_reset = user_data.get('last_reset', '2000-01-01')
                            if last_reset < current_reset.isoformat():
                                user_data['remains'] = 2
                                user_data['last_reset'] = current_reset.isoformat()
                                g.users[user_id_str] = user_data
                                await save_json_async('users.json', g.users)

                            if user_data.get('remains', 0) <= 0:
                                continue

                        error, success_text = await execute_like(
                            item['region'], item['uid'], user_id, group_id, auto=True
                        )
                        if error:
                            await log_action(f"Auto like failed for {user_id_str}, {item['region']} {item['uid']}: {error}")
                            continue

                        await deduct_group_remain(group_id)
                        if is_vip:
                            await deduct_vip_remain(user_id)
                        else:
                            user_data['remains'] -= 1
                            g.users[user_id_str] = user_data
                            await save_json_async('users.json', g.users)

                        item['last_liked'] = now.isoformat()
                        await save_json_async('autos.json', g.autos)
                        await log_action(f"Auto like executed for {item['region']} {item['uid']} by user {user_id_str} in group {group_id}")

                        try:
                            await bot.send_message(user_id, success_text, parse_mode="HTML", disable_web_page_preview=True)
                        except Exception as e:
                            await log_action(f"Failed to notify user {user_id_str} of auto like: {e}")

                    except Exception as e:
                        logger.error(f"Error processing auto-like for user {user_id_str}: {e}")
                        await log_action(f"Auto like error for user {user_id_str}: {e}")

            logger.info("Auto-like cycle completed")
        except Exception as e:
            logger.error(f"Error in auto_like_loop: {e}")
            await asyncio.sleep(60)  # Prevent tight loop on errors

# ---------------- ASYNC JSON SAVE ----------------
async def save_json_async(filename: str, data: Dict[str, Any]):
    try:
        await asyncio.get_event_loop().run_in_executor(None, save_json, filename, data)
    except Exception as e:
        logger.error(f"Failed to save JSON file {filename}: {e}")

# ---------------- ENTRYPOINT ----------------
async def main():
    try:
        # Start HTTP server
        asyncio.create_task(start_http_server())
        # Start auto_like_loop
        asyncio.create_task(auto_like_loop())
        # Start bot
        await bot.infinity_polling(timeout=20, request_timeout=600)
    except Exception as e:
        logger.error(f"Main loop error: {e}")
        raise
    finally:
        logger.info("Shutting down bot")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)