# app/vip.py
from datetime import datetime, timedelta, date
from app.globals import vips, users, save_json, get_reset_date
from app.logs import log_action

async def check_vip_status(user_id):
    user_id_str = str(user_id)
    if user_id_str not in vips:
        if user_id_str in users:
            users[user_id_str]['vip'] = False
            save_json('users.json', users)
        return False
    vip_data = vips[user_id_str]
    await reset_vip_if_needed(user_id)
    expiry = datetime.fromisoformat(vip_data['expiry_date'])
    if datetime.now() > expiry or vip_data.get('remains', 0) <= 0:
        if user_id_str in users:
            users[user_id_str]['vip'] = False
            save_json('users.json', users)
        del vips[user_id_str]
        save_json('vips.json', vips)
        await log_action(f"VIP status expired for user {user_id}")
        return False
    if user_id_str in users:
        users[user_id_str]['vip'] = True
        save_json('users.json', users)
    return True

async def reset_vip_if_needed(user_id):
    user_id_str = str(user_id)
    if user_id_str not in vips:
        return
    current_reset = get_reset_date()
    last_reset = vips[user_id_str].get('last_reset', '2000-01-01')
    if last_reset < current_reset:
        vips[user_id_str]['remains'] = vips[user_id_str].get('daily_limit', 0)
        vips[user_id_str]['last_reset'] = current_reset
        save_json('vips.json', vips)
        await log_action(f"VIP remains reset for user {user_id_str} to {vips[user_id_str]['remains']}")

async def deduct_vip_remain(user_id):
    user_id_str = str(user_id)
    if user_id_str in vips:
        vips[user_id_str]['remains'] -= 1
        save_json('vips.json', vips)