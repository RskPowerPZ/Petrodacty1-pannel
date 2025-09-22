# app/mode.py
from app.globals import grants, bot
from app.logs import log_action

async def check_channel_join(user_id, group_id):
    group_id_str = str(group_id)
    if grants.get(group_id_str, {}).get('approved', False):
        return True
    channel = grants.get(group_id_str, {}).get('promotion_channel')
    if not channel:
        return True  # No channel required
    try:
        member = await bot.get_chat_member(channel, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        await log_action(f"Channel join check failed for user {user_id} in group {group_id}: {str(e)}")
    return False