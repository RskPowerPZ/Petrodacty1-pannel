# admin/block.py
from config import OWNER_ID
from app.globals import blocks, users, save_json, bot
from app.logs import log_action
from datetime import datetime

LINK = "https://t.me/+Wj9XsjE7a4s1N2I1"
MAX_MSG_LEN = 4000  # Telegram safe limit

def register(bot):
    @bot.message_handler(commands=['block'])
    async def block_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        parts = message.text.split()[1:]
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            reason = ' '.join(parts) if parts else "No reason provided"
            from_user = message.reply_to_message.from_user
            name = from_user.first_name + (f" {from_user.last_name}" if from_user.last_name else "")
            username = from_user.username
        else:
            if not parts:
                await bot.reply_to(
                    message,
                    f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
                    f"<a href='{LINK}'>┃ 𝐔𝐬𝐚𝐠𝐞</a>\n"
                    f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\n"
                    f"<a href='{LINK}'>/block &lt;ᴜsᴇʀ_ɪᴅ&gt; [ʀᴇᴀsᴏɴ]</a>\n"
                    f"<a href='{LINK}'>ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ</a>",
                    parse_mode="HTML"
                )
                return
            try:
                user_id = int(parts[0])
                if user_id <= 0:
                    await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ_ɪᴅ, sʜᴏᴜʟᴅ ʙᴇ ᴘᴏsɪᴛɪᴠᴇ.")
                    return
            except ValueError:
                await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ_ɪᴅ.")
                return
            reason = ' '.join(parts[1:]) or "No reason provided"
            try:
                chat = await bot.get_chat(user_id)
                name = chat.first_name + (f" {chat.last_name}" if chat.last_name else "")
                username = chat.username
            except Exception as e:
                await log_action(f"Failed to fetch user {user_id}: {str(e)}")
                name = "Unknown"
                username = None

        user_id_str = str(user_id)
        blocks[user_id_str] = {
            'blocked_at': datetime.now().isoformat(),
            'reason': reason
        }
        user_data = users.get(user_id_str, {})
        user_data.update({
            'name': name,
            'username': username,
            'blocked': True
        })
        users[user_id_str] = user_data
        save_json('users.json', users)
        save_json('blocks.json', blocks)

        await log_action(f"User {user_id} blocked. Reason: {reason}")

        await bot.reply_to(
            message,
            f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
            f"<a href='{LINK}'>┃ 🚫 𝐔𝐬𝐞𝐫 𝐁𝐥𝐨𝐜𝐤𝐞𝐝</a>\n"
            f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\n"
            f"<a href='{LINK}'>ɪᴅ:</a> <code>{user_id}</code>\n"
            f"<a href='{LINK}'>ʀᴇᴀsᴏɴ:</a> <b>{reason}</b>",
            parse_mode="HTML"
        )

    @bot.message_handler(commands=['unblock'])
    async def unblock_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        parts = message.text.split()[1:]
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            if not parts:
                await bot.reply_to(
                    message,
                    f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
                    f"<a href='{LINK}'>┃ 𝐔𝐬𝐚𝐠𝐞</a>\n"
                    f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\n"
                    f"<a href='{LINK}'>/unblock &lt;ᴜsᴇʀ_ɪᴅ&gt;</a>\n"
                    f"<a href='{LINK}'>ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ</a>",
                    parse_mode="HTML"
                )
                return
            try:
                user_id = int(parts[0])
                if user_id <= 0:
                    await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ_ɪᴅ, sʜᴏᴜʟᴅ ʙᴇ ᴘᴏsɪᴛɪᴠᴇ.")
                    return
            except ValueError:
                await bot.reply_to(message, "❌ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ_ɪᴅ.")
                return

        user_id_str = str(user_id)
        if user_id_str in blocks:
            del blocks[user_id_str]
            save_json('blocks.json', blocks)
        if user_id_str in users:
            users[user_id_str]['blocked'] = False
            save_json('users.json', users)

        await log_action(f"User {user_id} unblocked.")

        await bot.reply_to(
            message,
            f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
            f"<a href='{LINK}'>┃ ✅ 𝐔𝐬𝐞𝐫 𝐔𝐧𝐛𝐥𝐨𝐜𝐤𝐞𝐝</a>\n"
            f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\n"
            f"<a href='{LINK}'>ɪᴅ:</a> <code>{user_id}</code>",
            parse_mode="HTML"
        )

    @bot.message_handler(commands=['blocklist'])
    async def blocklist_handler(message):
        if message.from_user.id != OWNER_ID:
            return

        if not blocks:
            await bot.reply_to(
                message,
                f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
                f"<a href='{LINK}'>┃ 𝐍𝐨 𝐁𝐥𝐨𝐜𝐤𝐞𝐝 𝐔𝐬𝐞𝐫𝐬</a>\n"
                f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>",
                parse_mode="HTML"
            )
            return

        lines = [
            f"<a href='{LINK}'>┏━━━━━━━⍟</a>\n"
            f"<a href='{LINK}'>┃ 🚫 𝐁𝐥𝐨𝐜𝐤𝐋𝐢𝐬𝐭</a>\n"
            f"<a href='{LINK}'>┗━━━━━━━━━━━⊛</a>\n\n"
        ]

        for uid, data in blocks.items():
            user = users.get(uid, {})
            name = user.get('name', 'Unknown')
            username = user.get('username')
            uname = f"@{username}" if username else "N/A"
            blocked_at = data.get("blocked_at", "N/A")
            reason = data.get("reason", "N/A")

            lines.append(
                f"<a href='{LINK}'>[⸙]</a> <b>{name}</b> {uname}\n"
                f"<a href='{LINK}'>[⸙]</a> ɪᴅ: <code>{uid}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> ʙʟᴏᴄᴋᴇᴅ ᴀᴛ: <code>{blocked_at}</code>\n"
                f"<a href='{LINK}'>[⸙]</a> ʀᴇᴀsᴏɴ: <b>{reason}</b>\n\n"
            )

        full_text = ''.join(lines)

        # Split into chunks without breaking HTML tags if possible, but for simplicity use fixed length
        for i in range(0, len(full_text), MAX_MSG_LEN):
            chunk = full_text[i:i+MAX_MSG_LEN]
            # Ensure chunk doesn't end mid-tag by trimming to last '>'
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