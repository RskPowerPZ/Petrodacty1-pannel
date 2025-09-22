# tools/remain.py
from app.block import not_blocked
from app.globals import users, grants, vips, save_json, bot, get_reset_date
from app.vip import check_vip_status
from app.grant import reset_group_if_needed

def register(bot):
    @bot.message_handler(commands=['remain'])
    @not_blocked
    async def remain_handler(message):
        user_id_str = str(message.from_user.id)
        group_id_str = str(message.chat.id)
        await reset_group_if_needed(message.chat.id)
        is_vip = await check_vip_status(message.from_user.id)
        if is_vip:
            personal = vips[user_id_str].get('remains', 0)
        else:
            current_reset = get_reset_date()
            last_reset = users.get(user_id_str, {}).get('last_reset', '2000-01-01')
            if last_reset < current_reset:
                users[user_id_str]['remains'] = 2
                users[user_id_str]['last_reset'] = current_reset
                save_json('users.json', users)
            personal = users.get(user_id_str, {}).get('remains', 0)
        group_remain = grants.get(group_id_str, {}).get('remain', 0)
        text = f"Personal remains: {personal}\nGroup remains: {group_remain}"
        await bot.reply_to(message, text)