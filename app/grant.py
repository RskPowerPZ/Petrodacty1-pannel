# app/grant.py
from app.globals import grants, save_json, get_reset_date
from app.logs import log_action

async def validate_grant(group_id):
    await reset_group_if_needed(group_id)
    group_id_str = str(group_id)
    if group_id_str not in grants:
        return False
    if grants[group_id_str].get('remain', 0) <= 0:
        return False
    return True

async def deduct_group_remain(group_id):
    group_id_str = str(group_id)
    grants[group_id_str]['remain'] -= 1
    save_json('grants.json', grants)
    await log_action(f"Group {group_id} remain deducted to {grants[group_id_str]['remain']}")

async def reset_group_if_needed(group_id):
    group_id_str = str(group_id)
    if group_id_str not in grants:
        return
    current_reset = get_reset_date()
    last_reset = grants[group_id_str].get('last_reset', '2000-01-01')
    if last_reset < current_reset:
        grants[group_id_str]['remain'] = grants[group_id_str].get('initial_remain', 0)
        grants[group_id_str]['last_reset'] = current_reset
        save_json('grants.json', grants)