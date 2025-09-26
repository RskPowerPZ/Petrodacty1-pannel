# admin/broadcast.py
import time
import asyncio
from datetime import timedelta
from config import OWNER_ID
from app.globals import users, grants, bot
from app.logs import log_action

LINK = "https://t.me/+63yIS-gsxsFiYmU1"

async def send_copy(uid, chat_id, msg_id):
    try:
        await bot.copy_message(uid, chat_id, msg_id)
        return True
    except Exception as e:
        await log_action(f"Failed to send broadcast to {uid}: {str(e)}")
        return False

def register(bot):
    @bot.message_handler(commands=['broad'])
    async def broadcast_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        if not message.reply_to_message:
            text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ ⚠️ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐄𝐫𝐫𝐨𝐫</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> ❌ Reply to a message to broadcast!
"""
            await bot.reply_to(message, text, parse_mode="HTML")
            return

        broadcast_msg = message.reply_to_message
        all_targets = list(set(users.keys()) | set(grants.keys()))
        total = len(all_targets)

        if total == 0:
            await bot.reply_to(message, "No recipients found.", parse_mode="HTML")
            return

        start_msg = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 🚀 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐓𝐨𝐭𝐚𝐥 𝐑𝐞𝐜𝐢𝐩𝐢𝐞𝐧𝐭𝐬 ➳ <code>{total}</code>\n
<a href="{LINK}">[⸙]</a> 𝐒𝐭𝐚𝐭𝐮𝐬 ➳ In Progress...
"""
        status_message = await bot.reply_to(message, start_msg, parse_mode="HTML")

        sent_count = 0
        fail_count = 0
        start = time.perf_counter()

        batch_size = 20  # Increased for efficiency, but still safe
        delay_between_batches = 1  # seconds to avoid rate limits

        for i in range(0, total, batch_size):
            batch = all_targets[i:i+batch_size]
            tasks = [send_copy(int(uid), message.chat.id, broadcast_msg.message_id) for uid in batch]
            results = await asyncio.gather(*tasks)
            for result in results:
                if result:
                    sent_count += 1
                else:
                    fail_count += 1

            # Update progress
            progress = int((sent_count + fail_count) * 100 / total)
            progress_text = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ 🚀 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐓𝐨𝐭𝐚𝐥 𝐑𝐞𝐜𝐢𝐩𝐢𝐞𝐧𝐭𝐬 ➳ <code>{total}</code>\n
<a href="{LINK}">[⸙]</a> 𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 ➳ <code>{progress}%</code>\n
<a href="{LINK}">[⸙]</a> 𝐒𝐞𝐧𝐭 ➳ <code>{sent_count}</code>\n
<a href="{LINK}">[⸙]</a> 𝐅𝐚𝐢𝐥𝐞𝐝 ➳ <code>{fail_count}</code>
"""
            await bot.edit_message_text(progress_text, message.chat.id, status_message.message_id, parse_mode="HTML")

            await asyncio.sleep(delay_between_batches)

        total_seconds = time.perf_counter() - start
        hours, remainder = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(remainder, 60)

        time_str = ""
        if hours > 0:
            time_str += f"{hours} Hour(s) "
        if minutes > 0:
            time_str += f"{minutes} Minute(s) "
        time_str += f"{seconds} Second(s)"

        success_rate = int((sent_count * 100 / total) if total > 0 else 0)

        done = f"""
<a href="{LINK}">┏━━━━━━━⍟</a>
<a href="{LINK}">┃ ✅ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐑𝐞𝐩𝐨𝐫𝐭</a>
<a href="{LINK}">┗━━━━━━━━━━━⊛</a>

<a href="{LINK}">[⸙]</a> 𝐓𝐨𝐭𝐚𝐥 ➳ <code>{total}</code>\n
<a href="{LINK}">[⸙]</a> 𝐒𝐞𝐧𝐭 ➳ <code>{sent_count}</code>\n
<a href="{LINK}">[⸙]</a> 𝐅𝐚𝐢𝐥𝐞𝐝 ➳ <code>{fail_count}</code>\n
<a href="{LINK}">[⸙]</a> 𝐒𝐮𝐜𝐜𝐞𝐬𝐬 ➳ <code>{success_rate}%</code>\n
<a href="{LINK}">[⸙]</a> 𝐓𝐢𝐦𝐞 ➳ <code>{time_str}</code>\n
[⸙] 𝐃𝐞𝐯 ➳ <a href="tg://user?id=7470004765">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>\n
"""
        await log_action(f"Broadcast finished. Sent: {sent_count}, Failed: {fail_count}, Total: {total}")
        await bot.edit_message_text(done, message.chat.id, status_message.message_id, parse_mode="HTML", disable_web_page_preview=True)