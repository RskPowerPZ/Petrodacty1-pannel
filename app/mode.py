# app/mode.py
from app.globals import grants, bot
from app.logs import log_action

VALID_STATUSES = {"member", "administrator", "creator", "restricted"}

async def check_channel_join(user_id, group_id) -> bool:
    """
    Check if a user is required to join a promotion channel for the group,
    and if yes, whether they have joined. Returns True if allowed, else False.
    """
    group_id_str = str(group_id)

    group_data = grants.get(group_id_str, {})
    if group_data.get("approved", False):
        return True

    channel = group_data.get("promotion_channel")
    if not channel:
        # no channel requirement
        return True

    # Ensure bot has get_chat_member
    if not hasattr(bot, "get_chat_member"):
        await log_action(f"[WARN] Bot instance missing get_chat_member() when checking channel {channel}")
        return True  # fail-open instead of blocking everyone

    try:
        member = await bot.get_chat_member(channel, user_id)

        status = getattr(member, "status", None)
        if status in VALID_STATUSES:
            return True

        await log_action(
            f"User {user_id} is not a valid member of channel {channel} "
            f"(status={status!r}) for group {group_id_str}"
        )

    except Exception as e:
        await log_action(
            f"Channel join check failed for user {user_id} in group {group_id_str}, "
            f"channel {channel}: {type(e).__name__}: {e}"
        )

    return False