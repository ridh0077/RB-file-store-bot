import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# --- RENDER KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home(): return "RBmods Bot is Live!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): threading.Thread(target=run_flask).start()

load_dotenv()

# Variables
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
# ID ko clean karne ke liye strip() use kiya hai
LOG_CHANNEL = int(str(os.environ.get("LOG_CHANNEL", "0")).strip())

bot = Client("RBFileStore", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- SETTINGS ---
WELCOME_TEXT = "Hello {name}!\n\nWelcome to my **RBmods channel** bot. Aapka swagat hai!\n\nMain aapki files ka link bana kar de sakta hoon."
JOIN_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("Join RBmods 📢", url="https://t.me/rbmodschats")]])

# 1. Start Command
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    # Link handling
    if len(m.command) > 1:
        file_id = m.command[1]
        try:
            await c.copy_message(chat_id=m.from_user.id, from_chat_id=LOG_CHANNEL, message_id=int(file_id))
        except Exception:
            await m.reply_text("❌ Error: File nahi mili.")
        return

    # Welcome Message
    await m.reply_text(
        text=WELCOME_TEXT.format(name=m.from_user.first_name),
        reply_markup=JOIN_BUTTON
    )

# 2. File to Link (Admin Only)
@bot.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def gen_link(c, m):
    if m.from_user.id != ADMIN_ID:
        return

    try:
        # Get File Name
        file_name = "File"
        if m.document:
            file_name = m.document.file_name
        elif m.video:
            file_name = m.video.file_name or "Video"
        elif m.audio:
            file_name = m.audio.file_name or "Audio"
        elif m.photo:
            file_name = "Photo"

        # Copy to channel
        log_msg = await m.copy(LOG_CHANNEL)
        bot_info = await c.get_me()
        share_link = f"https://t.me/{bot_info.username}?start={log_msg.id}"
        
        # Reply with name and link
        await m.reply_text(
            f"✅ **Aapka File Link Taiyar Hai:**\n\n"
            f"📂 **Name:** `{file_name}`\n"
            f"🔗 **Link:** `{share_link}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share Link 🔗", url=f"https://t.me/share/url?url={share_link}")]])
        )
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}\n\nCheck karein ki bot channel mein admin hai ya nahi.")

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.run()
