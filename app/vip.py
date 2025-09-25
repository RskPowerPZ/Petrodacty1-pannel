# app/vip.py
from datetime import datetime, date, timedelta
from app.globals import vips, users, save_json, get_reset_date
from app.logs import log_action
from typing import Optional, Union

def _to_date(d: Union[str, date]) -> date:
    """Convert either a date or ISO 'YYYY-MM-DD' string to a date object."""
    if isinstance(d, date) and not isinstance(d, datetime):
        return d
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        try:
            return datetime.fromisoformat(d).date()
        except Exception:
            # fallback for plain YYYY-MM-DD
            return datetime.strptime(d, "%Y-%m-%d").date()
    raise ValueError("Unsupported date format")

def _parse_iso_datetime(s: Optional[str]) -> Optional[datetime]:
    """Parse an ISO datetime or date string. Return None on failure."""
    if not s:
        return None
    try:
        # handles both date-only "YYYY-MM-DD" and full ISO datetime
        if len(s) == 10:
            return datetime.fromisoformat(s + "T00:00:00")
        return datetime.fromisoformat(s)
    except Exception:
        try:
            # last-resort: try parsing date portion
            return datetime.strptime(s.split("T")[0], "%Y-%m-%d")
        except Exception:
            return None

async def check_vip_status(user_id) -> bool:
    """
    Return True if user is an active VIP (not expired and has remains > 0).
    Keeps users.json and vips.json in sync for the 'vip' flag where appropriate.
    """
    user_id_str = str(user_id)

    # Ensure any daily reset is applied first
    await reset_vip_if_needed(user_id)

    if user_id_str not in vips:
        # mark non-vip in users if present
        if user_id_str in users:
            users[user_id_str]['vip'] = False
            save_json('users.json', users)
        return False

    vip_data = vips[user_id_str]

    # parse expiry safely
    expiry_dt = _parse_iso_datetime(vip_data.get('expiry_date'))
    if expiry_dt is None:
        # malformed expiry -> expire VIP
        vips.pop(user_id_str, None)
        save_json('vips.json', vips)
        await log_action(f"VIP data malformed/expired for user {user_id_str} (bad expiry_date).")
        if user_id_str in users:
            users[user_id_str]['vip'] = False
            save_json('users.json', users)
        return False

    # compare aware vs naive datetimes safely
    now = datetime.now(tz=expiry_dt.tzinfo) if expiry_dt.tzinfo else datetime.now()

    if now > expiry_dt:
        vips.pop(user_id_str, None)
        save_json('vips.json', vips)
        await log_action(f"VIP status expired for user {user_id_str} (expiry reached).")
        if user_id_str in users:
            users[user_id_str]['vip'] = False
            save_json('users.json', users)
        return False

    # check remains
    remains = int(vip_data.get('remains', 0))
    if remains <= 0:
        vips.pop(user_id_str, None)
        save_json('vips.json', vips)
        await log_action(f"VIP status expired for user {user_id_str} (no remains).")
        if user_id_str in users:
            users[user_id_str]['vip'] = False
            save_json('users.json', users)
        return False

    # everything fine -> mark user VIP in users (if exists)
    if user_id_str in users:
        users[user_id_str]['vip'] = True
        save_json('users.json', users)
    return True

async def reset_vip_if_needed(user_id):
    """
    Reset daily remains for this VIP if last_reset < current reset date.
    get_reset_date() may return a date or an ISO date string; handle both.
    """
    user_id_str = str(user_id)
    if user_id_str not in vips:
        return

    # get current reset date (support both str and date)
    current_reset_raw = get_reset_date()
    try:
        current_reset = _to_date(current_reset_raw)
    except Exception:
        # if get_reset_date returned something unexpected, don't reset
        await log_action(f"get_reset_date returned unexpected value: {current_reset_raw}")
        return

    last_reset_raw = vips[user_id_str].get('last_reset', '2000-01-01')
    try:
        last_reset = _to_date(last_reset_raw)
    except Exception:
        # if malformed, force a reset
        last_reset = date(2000, 1, 1)

    if last_reset < current_reset:
        # set remains to daily_limit (fallback 0)
        new_remains = int(vips[user_id_str].get('daily_limit', 0))
        vips[user_id_str]['remains'] = new_remains
        vips[user_id_str]['last_reset'] = current_reset.isoformat()
        save_json('vips.json', vips)
        await log_action(f"VIP remains reset for user {user_id_str} to {new_remains}")

async def deduct_vip_remain(user_id) -> Optional[int]:
    """
    Deduct one remain for the VIP. Returns new remains (int) or None if user not VIP.
    Ensures remains never goes below 0.
    """
    user_id_str = str(user_id)
    if user_id_str not in vips:
        return None

    # ensure reset was applied before deducting
    await reset_vip_if_needed(user_id)

    remains = int(vips[user_id_str].get('remains', 0))
    if remains <= 0:
        # nothing to deduct
        vips[user_id_str]['remains'] = 0
        save_json('vips.json', vips)
        await log_action(f"Attempted to deduct VIP remain for user {user_id_str} but remains already 0.")
        return 0

    vips[user_id_str]['remains'] = remains - 1
    save_json('vips.json', vips)
    await log_action(f"Deducted 1 VIP remain for user {user_id_str}. New remains: {vips[user_id_str]['remains']}")
    return vips[user_id_str]['remains']