# app/response.py
API_ERROR = "❌ API error: {}"
INVALID_INPUT = "⚠️ Wrong format! Use: /like {region} {uid} or /add {region} {uid}"
DAILY_LIMIT = "⚠️ You have reached your daily limit of 2 likes."
BLOCKED = "🚫 You are blocked by admin. Contact support."
SERVER_BUSY = "⚠️ Server is busy, try again later."
MAXED_OUT = "⚠️ UID already maxed out."
SUCCESS = """<a href="https://t.me/+Wj9XsjE7a4s1N2I1">┏━━━━━━━⍟</a>
<a href="https://t.me/+Wj9XsjE7a4s1N2I1">┃ ✅ 𝐋𝐢𝐤𝐞 𝐒𝐮𝐜𝐜𝐞𝐬𝐬</a>
<a href="https://t.me/+Wj9XsjE7a4s1N2I1">┗━━━━━━━━━━━⊛</a>

<a href="https://t.me/+Wj9XsjE7a4s1N2I1">[⸙]</a> ɴɪᴄᴋɴᴀᴍᴇ ➳ <b>{nickname}</b>\n
<a href="https://t.me/+Wj9XsjE7a4s1N2I1">[⸙]</a> ᴜɪᴅ ➳ <code>{uid}</code>\n
<a href="https://t.me/+Wj9XsjE7a4s1N2I1">[⸙]</a> ʙᴇғᴏʀᴇ ➳ <b>{before}</b>\n
<a href="https://t.me/+Wj9XsjE7a4s1N2I1">[⸙]</a> ᴀғᴛᴇʀ ➳ <b>{after}</b>\n
<a href="https://t.me/+Wj9XsjE7a4s1N2I1">[⸙]</a> ɢɪᴠᴇɴ ➳ <b>{given}</b>\n
<a href="https://t.me/+Wj9XsjE7a4s1N2I1">[⸙]</a> ᴛɪᴍᴇ ➳ <code>{time}</code>\n
[⸙] ʙᴏᴛ ʙʏ ➳ <a href="https://t.me/+Wj9XsjE7a4s1N2I1">⏤꯭𖣐᪵𖡡꯭𝆭𐎓⏤𝐑𝐚𝐡𝐮𝐥 ꯭𖠌𐎙ꭙ⁷𖡡</a>"""