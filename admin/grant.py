# admin/grant.py
from typing import Dict, Any
import json
from config import OWNER_ID
from app.globals import grants, save_json, bot, get_reset_date
from app.logs import log_action

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"
MAX_MSG_LEN = 4000  # Telegram safe message length limit

# Bot attribution text
BOT_BY_TEXT = '[⸙]  𝐃𝐞𝐯  ➳ <a href="tg://user?id=7439897927">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n'

# Usage help text
USAGE_TEXT = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 𝐆𝐫𝐚𝐧𝐭 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐇𝐞𝐥𝐩</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐔𝐬𝐚𝐠𝐞 ➳ <code>/grant &lt;group_id&gt; &lt;remaining_requests&gt;</code>
<a href="{LINK}">[⸙]</a> 𝐄𝐱𝐚𝐦𝐩𝐥𝐞 ➳ <code>/grant -1001234567890 50</code>
<a href="{LINK}">[⸙]</a> 𝐃𝐞𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧 ➳ Adds or updates a grant for a group.
{BOT_BY_TEXT}
"""

def register(bot):
    """Register grant-related command handlers for the bot."""
    
    @bot.message_handler(commands=['grant'])
    async def grant_handler(message):
        """
        Handle /grant command to add or update group grants.
        Only accessible to the bot owner.
        """
        if message.from_user.id != OWNER_ID:
            await bot.reply_to(message, "❌ Unauthorized access. Owner only.")
            return

        parts = message.text.split(maxsplit=2)[1:]  # Safer split with maxsplit
        if len(parts) < 2:
            await bot.reply_to(message, USAGE_TEXT, parse_mode="HTML", disable_web_page_preview=True)
            return

        try:
            group_id = int(parts[0])
            remain = int(parts[1])
            
            # Validate inputs
            if group_id >= 0:
                await bot.reply_to(message, "❌ Group ID must be negative.", parse_mode="HTML")
                return
            if remain < 0:
                await bot.reply_to(message, "❌ Remaining requests must be non-negative.", parse_mode="HTML")
                return
                
        except ValueError:
            await bot.reply_to(message, "❌ Invalid format for group_id or remaining requests.", parse_mode="HTML")
            return

        try:
            chat = await bot.get_chat(group_id)
            group_name = chat.title or 'Unnamed Group'
        except Exception as e:
            await bot.reply_to(message, f"❌ Invalid group ID or bot not in group: {str(e)}", parse_mode="HTML")
            return

        group_id_str = str(group_id)
        try:
            grants[group_id_str] = {
                'name': group_name,
                'initial_remain': remain,
                'remain': remain,
                'promotion_channel': None,
                'approved': False,
                'last_reset': get_reset_date()
            }
            save_json('grants.json', grants)
            await log_action(f"Grant added for group {group_id} ({group_name}) with {remain} remains by user {message.from_user.id}")
        except Exception as e:
            await bot.reply_to(message, f"❌ Failed to save grant: {str(e)}", parse_mode="HTML")
            return

        reply_text = f"""
<a href='{LINK}'>┏━━━━━━━⍟</a>
<a href='{LINK}'>┃ ✅ 𝐆𝐫𝐚𝐧𝐭 𝐀𝐝𝐝𝐞𝐝</a>
<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>

<a href='{LINK}'>[⸙]</a> 𝐆𝐫𝐨𝐮𝐩 ➳ <b>{group_name}</b>
<a href='{LINK}'>[⸙]</a> 𝐑𝐞𝐦𝐚𝐢𝐧𝐬 ➳ <b>{remain}</b>
{BOT_BY_TEXT}
"""
        await bot.reply_to(message, reply_text, parse_mode='HTML', disable_web_page_preview=True)

    @bot.message_handler(commands=['grants'])
    async def grants_handler(message):
        """
        Handle /grants command to list all group grants.
        Only accessible to the bot owner.
        """
        if message.from_user.id != OWNER_ID:
            await bot.reply_to(message, "❌ Unauthorized access. Owner only.", parse_mode="HTML")
            return

        if not grants:
            await bot.reply_to(
                message,
                f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n<a href='{LINK}'>┃ 𝐍𝐨 𝐠𝐫𝐚𝐧𝐭𝐬 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞</a>\n<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>",
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            return

        lines = [f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n<a href='{LINK}'>┃ 𝐆𝐫𝐚𝐧𝐭𝐬 𝐋𝐢𝐬𝐭</a>\n<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n"]
        for gid, data in grants.items():
            name = data.get('name', 'Unnamed Group')
            remain = data.get('remain', 0)
            link = data.get('promotion_channel', 'N/A')
            line = (
                f"<a href='{LINK}'>[⸙]</a> <b>{name}</b>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐈𝐃: <code>{gid}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐑𝐞𝐦𝐚𝐢𝐧𝐬: <b>{remain}</b>\n"
                f"<a href='{LINK}'>[⸙]</a> 𝐈𝐧𝐯𝐢𝐭𝐞: {link}\n"
                f"{BOT_BY_TEXT}\n"
            )
            lines.append(line)

        full_text = ''.join(lines)
        
        # Split messages efficiently while respecting MAX_MSG_LEN
        current_message = ""
        for line in lines:
            if len(current_message) + len(line) > MAX_MSG_LEN:
                await bot.reply_to(message, current_message, parse_mode='HTML', disable_web_page_preview=True)
                current_message = line
            else:
                current_message += line

        # Send any remaining text
        if current_message:
            await bot.reply_to(message, current_message, parse_mode='HTML', disable_web_page_preview=True)