# admin/grant.py
from config import OWNER_ID
from app.globals import grants, save_json, bot, get_reset_date
from app.logs import log_action
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

LINK = "https://t.me/+63yIS-gsxsFiYmU1"  # Aligned with other modules
MAX_MSG_LEN = 4000  # Telegram safe limit

# Bot attribution text (aligned with other modules)
BOT_BY_TEXT = '[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7470004765">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n'

USAGE_TEXT = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐆𝐫𝐚𝐧𝐭 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐇𝐞𝐥𝐩</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐚𝐠𝐞 ➳ <code>/grant &lt;group_id&gt; &lt;remaining_requests&gt;</code>\n
<a href="{LINK}">[⸙]</a> 𝐄𝐱𝐚𝐦𝐩𝐥𝐞 ➳ <code>/grant -1001234567890 50</code>\n
<a href="{LINK}">[⸙]</a> 𝐃𝐞𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 ➳ Adds or updates a grant for a group.\n
{BOT_BY_TEXT}
"""

def register(bot):
    @bot.message_handler(commands=['grant'])
    async def grant_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        parts = message.text.split()[1:]
        if len(parts) < 2:
            await bot.reply_to(message, USAGE_TEXT, parse_mode="HTML", disable_web_page_preview=True)
            return

        try:
            group_id = int(parts[0])
            remain = int(parts[1])
            if group_id >= 0:
                await bot.reply_to(message, "❌ Invalid group_id, should be negative.", parse_mode="HTML")
                return
            if remain < 0:
                await bot.reply_to(message, "❌ Remaining requests cannot be negative.", parse_mode="HTML")
                return
        except ValueError:
            await bot.reply_to(message, "❌ Invalid numbers for group_id or remain.", parse_mode="HTML")
            return

        try:
            chat = await bot.get_chat(group_id)
            group_name = chat.title or 'Unnamed'
        except Exception as e:
            await bot.reply_to(message, "❌ Invalid group_id or bot not in group.", parse_mode="HTML")
            await log_action(f"Failed to fetch group {group_id}: {str(e)}")
            return

        group_id_str = str(group_id)
        grants[group_id_str] = {
            'name': group_name,
            'initial_remain': remain,
            'remain': remain,
            'promotion_channel': None,
            'approved': False,
            'last_reset': get_reset_date()
        }
        save_json('grants.json', grants)
        await log_action(f"Grant added for group {group_id} with {remain} remains.")

        reply_text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ ✅ 𝐆𝐫𝐚𝐧𝐭 𝐀𝐝𝐝𝐞𝐝</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐆𝐫𝐨𝐮𝐩 ➳ <b>{group_name}</b>\n
<a href="{LINK}">[⸙]</a> 𝐑𝐞𝐦𝐚𝐢𝐧𝐬 ➳ <b>{remain}</b>\n
{BOT_BY_TEXT}
"""
        await bot.reply_to(message, reply_text, parse_mode="HTML", disable_web_page_preview=True)

    @bot.message_handler(commands=['grants'])
    async def grants_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        if not grants:
            await bot.reply_to(
                message,
                f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐍𝐨 𝐆𝐫𝐚𝐧𝐭𝐬 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>
{BOT_BY_TEXT}
""",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            return

        lines = [f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐆𝐫𝐚𝐧𝐭𝐬 𝐋𝐢𝐬𝐭</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>\n
"""]

        for gid, data in grants.items():
            name = data.get('name', 'Unnamed')
            remain = data.get('remain', 0)
            link = data.get('promotion_channel', 'N/A')
            approved = 'Yes' if data.get('approved', False) else 'No'
            line = (
                f"<a href='{LINK}'>[⸙]</a> <b>{name}</b>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐈𝐃 ➳ <code>{gid}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐑𝐞𝐦𝐚𝐢𝐧𝐬 ➳ <b>{remain}</b>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐈𝐧𝐯𝐢𝐭𝐞 ➳ <b>{link}</b>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ➳ <b>{approved}</b>\n\n"
            )
            lines.append(line)

        lines.append(BOT_BY_TEXT)
        full_text = ''.join(lines)

        # Split into chunks to respect MAX_MSG_LEN
        for i in range(0, len(full_text), MAX_MSG_LEN):
            chunk = full_text[i:i+MAX_MSG_LEN]
            # Ensure chunk doesn't cut off in the middle of an HTML tag
            if i + MAX_MSG_LEN < len(full_text):
                last_gt = chunk.rfind('>')
                if last_gt != -1:
                    chunk = chunk[:last_gt+1]
            await bot.reply_to(
                message,
                chunk,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        await log_action(f"Grants list requested by user {message.from_user.id}")