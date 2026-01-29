import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# --- RENDER KEEP ALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "RBmods File Store is Online!"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive(): threading.Thread(target=run_flask).start()

load_dotenv()

# Variables (Render se fetch honge)
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))

bot = Client("RBFileStore", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 1. Start Command (Link handling + Welcome)
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    # Agar kisi ne link par click kiya hai (Example: /start 123)
    if len(m.command) > 1:
        file_id = m.command[1]
        try:
            await c.copy_message(chat_id=m.from_user.id, from_chat_id=LOG_CHANNEL, message_id=int(file_id))
        except Exception as e:
            await m.reply_text("❌ Error: File nahi mili ya link purana hai.")
        return

    # Normal Welcome Message
    name = m.from_user.first_name
    await m.reply_text(
        text=f"Hello {name}!\n\nWelcome to **RBmods channel**.\n\nMain aapko files ka link bana kar de sakta hoon. Sirf Admin hi link bana sakta hai.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel 📢", url="https://t.me/RBmods")]])
    )

# 2. File to Link Generator (Sirf Admin bhej sakta hai)
@bot.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def gen_link(c, m):
    if m.from_user.id != ADMIN_ID:
        return # Do nothing for non-admins to avoid spam

    # File ko Log Channel mein bhej raha hai
    try:
        log_msg = await m.copy(LOG_CHANNEL)
        bot_info = await c.get_me()
        share_link = f"https://t.me/{bot_info.username}?start={log_msg.id}"
        
        await m.reply_text(
            f"✅ **Aapka File Link Taiyar Hai:**\n\n`{share_link}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share Link 🔗", url=f"https://t.me/share/url?url={share_link}")]])
        )
    except Exception as e:
        await m.reply_text(f"❌ Error: Kya aapne bot ko channel mein admin banaya hai? \n\nDetails: {e}")

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting...")
    bot.run()
