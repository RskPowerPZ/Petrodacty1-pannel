import json
from pathlib import Path
from datetime import datetime, timezone
from app.globals import bot

# Link (you asked to use this)
LINK = "https://t.me/+63yIS-gsxsFiYmU1"

# Files
USERS_FILE = Path("data/users.json")
VIPS_FILE = Path("data/vips.json")
BLOCKS_FILE = Path("data/blocks.json")

BOT_BY_TEXT = '𝐃𝐞𝐯 ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>'


def _parse_iso_datetime(s: str):
    """Try to parse ISO datetime. Returns datetime or None."""
    if not s:
        return None
    try:
        # fromisoformat handles both date and datetime, and offset-aware strings
        return datetime.fromisoformat(s)
    except Exception:
        # try a crude fallback for trailing Z
        try:
            if s.endswith("Z"):
                return datetime.fromisoformat(s[:-1])
        except Exception:
            return None
    return None


def is_vip_local(user_id: int) -> bool:
    """Return True if user_id exists in vips.json and expiry_date > now (UTC)."""
    if not VIPS_FILE.exists():
        return False

    user_key = str(user_id)
    try:
        with open(VIPS_FILE, "r", encoding="utf-8") as f:
            vips = json.load(f)
    except Exception as e:
        print(f"[is_vip_local] Error loading vips.json: {e}")
        return False

    entry = vips.get(user_key) or vips.get(int(user_key))  # handle possible int keys
    if not entry:
        return False

    expiry_raw = entry.get("expiry_date")
    if not expiry_raw:
        # no expiry set -> treat as VIP
        return True

    expiry_dt = _parse_iso_datetime(expiry_raw)
    if expiry_dt is None:
        # can't parse -> be generous and treat as VIP
        return True

    # Normalize expiry to naive UTC for comparison
    now_utc = datetime.utcnow().replace(tzinfo=None)
    if expiry_dt.tzinfo is not None:
        expiry_utc_naive = expiry_dt.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        expiry_utc_naive = expiry_dt

    return expiry_utc_naive > now_utc


def get_user_remains(user_id: int, is_vip: bool = None) -> int:
    """
    Return remaining requests for the user.
    If is_vip is None, automatically detect VIP status.
    """
    if is_vip is None:
        is_vip = is_vip_local(user_id)

    user_key = str(user_id)
    try:
        if is_vip and VIPS_FILE.exists():
            with open(VIPS_FILE, "r", encoding="utf-8") as f:
                vips = json.load(f)
            entry = vips.get(user_key) or vips.get(int(user_key))
            if not entry:
                return 0
            # prefer explicit remains, fallback to daily_limit
            return int(entry.get("remains", entry.get("daily_limit", 0)))
        else:
            # normal user remains from users.json
            if USERS_FILE.exists():
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    users = json.load(f)
                entry = users.get(user_key) or users.get(int(user_key))
                if not entry:
                    return 0
                return int(entry.get("remains", 0))
    except Exception as e:
        print(f"[get_user_remains] Error: {e}")
    return 0


def is_user_blocked(user_id: int) -> bool:
    """
    Robust check across possible blocks.json formats:
    - dict of keys
    - list of ids
    - single string/id
    """
    if not BLOCKS_FILE.exists():
        return False

    try:
        with open(BLOCKS_FILE, "r", encoding="utf-8") as f:
            blocks = json.load(f)
    except Exception as e:
        print(f"[is_user_blocked] Error loading blocks.json: {e}")
        return False

    user_key = str(user_id)

    if isinstance(blocks, dict):
        # keys or values could contain ids
        if user_key in blocks:
            return True
        # also check values just in case structure is { "123": {"reason": "..."} }
        try:
            return any(user_key == str(k) or user_key == str(v) for k, v in blocks.items())
        except Exception:
            return False

    if isinstance(blocks, list):
        return user_key in blocks or user_id in blocks

    if isinstance(blocks, (str, int)):
        return user_key == str(blocks)

    # fallback: try stringifying and searching
    try:
        return user_key in json.dumps(blocks)
    except Exception:
        return False


def register(bot):
    @bot.message_handler(commands=['info'])
    async def userinfo_handler(message):
        # target user: replied-to user or message sender
        if message.reply_to_message:
            user = message.reply_to_message.from_user
        else:
            user = message.from_user

        user_id = user.id
        user_id_str = str(user_id)

        # Use local VIP check (reliable)
        is_vip = is_vip_local(user_id)
        blocked_val = is_user_blocked(user_id)
        remains = get_user_remains(user_id, is_vip)

        # Fetch additional VIP details (optional, for debugging)
        vip_entry = None
        if VIPS_FILE.exists():
            try:
                with open(VIPS_FILE, "r", encoding="utf-8") as f:
                    vips = json.load(f)
                vip_entry = vips.get(user_id_str) or vips.get(int(user_id_str))
            except Exception:
                vip_entry = None

        expiry_text = vip_entry.get("expiry_date") if vip_entry else "N/A"
        bought_text = vip_entry.get("bought_date") if vip_entry else "N/A"
        daily_limit = vip_entry.get("daily_limit") if vip_entry else "N/A"

        # Basic details
        name = user.first_name or 'Unknown'
        username = f"@{user.username}" if user.username else "N/A"
        chat_id = message.chat.id

        # Status
        status = 'ᴀᴅᴍɪɴ' if user.id in [7470004765] else 'ᴜsᴇʀ'
        vip_text = 'ᴛʀᴜᴇ' if is_vip else 'ғᴀʟsᴇ'
        blocked_text = 'ᴛʀᴜᴇ' if blocked_val else 'ғᴀʟsᴇ'

        text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐔𝐬𝐞𝐫 𝐈𝐧𝐟ᴏ</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐍𝐚𝐦𝐞 ➳ <b>{name}</b>
<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐞𝐫𝐧ᴀᴍᴇ ➳ <b>{username}</b>
<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐞ʀ 𝐈ᴅ ➳ <code>{user_id_str}</code>
<a href="{LINK}">[⸙]</a> 𝐂ʜᴀᴛ 𝐈ᴅ ➳ <code>{chat_id}</code>
<a href="{LINK}">[⸙]</a> 𝐒ᴛᴀᴛᴜs ➳ <b>{status}</b>
<a href="{LINK}">[⸙]</a> 𝐕ɪᴘ ➳ <b>{vip_text}</b>
<a href="{LINK}">[⸙]</a> 𝐁ʟᴏᴄᴋᴇᴅ ➳ <b>{blocked_text}</b>
<a href="{LINK}">[⸙]</a> 𝐑ᴇᴍᴀɪɴɪɴɢ 𝐑ᴇǫᴜᴇsᴛs ➳ <b>{remains}</b>

<a href="{LINK}">[⸙]</a> 𝐕𝐈𝐏 𝐅𝐫𝐨𝐦 ➳ <b>{bought_text}</b>
<a href="{LINK}">[⸙]</a> 𝐕𝐈𝐏 𝐄𝐱𝐩𝐢𝐫𝐲 ➳ <b>{expiry_text}</b>
<a href="{LINK}">[⸙]</a> 𝐃𝐚𝐢𝐥𝐲 𝐋𝐢𝐦𝐢𝐭 ➳ <b>{daily_limit}</b>

{BOT_BY_TEXT}
"""

        await bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)