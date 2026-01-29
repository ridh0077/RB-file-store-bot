import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# --- RENDER KEEP ALIVE SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "RBmods Bot is Live and Running!"

def run_flask():
    # Render default port 8080 use karta hai
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

# --- BOT CONFIGURATION ---
load_dotenv()

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
LOG_CHANNEL = int(str(os.environ.get("LOG_CHANNEL", "0")).strip())

bot = Client("RBFileStore", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Settings for messages
WELCOME_TEXT = "Hello {name}!\n\nWelcome to my **RBmods channel** bot. Aapka swagat hai!\n\nMain aapki files ka link bana kar de sakta hoon."
JOIN_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("Join RBmods 📢", url="https://t.me/rbmodschats")]])

# Global variable to store bot username to avoid flood waits
BOT_UNAME = None

# --- COMMANDS & HANDLERS ---

# 1. Start Command (Handles links and normal start)
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    # Check if there's a file ID in the command (Example: /start 14)
    if len(m.command) > 1:
        file_id = m.command[1]
        try:
            # Copy file from Log Channel to the user who clicked the link
            await c.copy_message(
                chat_id=m.from_user.id, 
                from_chat_id=LOG_CHANNEL, 
                message_id=int(file_id)
            )
        except Exception:
            await m.reply_text("❌ Error: File nahi mili ya delete ho gayi hai.")
        return

    # Normal Welcome Message
    await m.reply_text(
        text=WELCOME_TEXT.format(name=m.from_user.first_name),
        reply_markup=JOIN_BUTTON
    )

# 2. Total Files Stats Command (Only for Admin)
@bot.on_message(filters.command("total") & filters.user(ADMIN_ID))
async def total_files_handler(c, m):
    try:
        # Get the total number of messages in the Log Channel
        count = await c.get_chat_history_count(LOG_CHANNEL)
        await m.reply_text(f"📊 **Bot Stats:**\n\nTotal Apps/Files stored: `{count}`")
    except Exception as e:
        await m.reply_text(f"❌ Error while fetching stats: {e}")

# 3. File to Link Generator (Only for Admin)
@bot.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def gen_link(c, m):
    global BOT_UNAME
    # Check if the sender is the Admin
    if m.from_user.id != ADMIN_ID:
        return

    try:
        # Fetch bot username once and store it
        if not BOT_UNAME:
            me = await c.get_me()
            BOT_UNAME = me.username

        # Get the File Name based on the type
        file_name = "File"
        if m.document:
            file_name = m.document.file_name
        elif m.video:
            file_name = m.video.file_name or "Video"
        elif m.audio:
            file_name = m.audio.file_name or "Audio"
        elif m.photo:
            file_name = "Photo"

        # Copy the message to the Log Channel to store it permanently
        log_msg = await m.copy(LOG_CHANNEL)
        
        # Create the unique start link using the message ID from the Log Channel
        share_link = f"https://t.me/{BOT_UNAME}?start={log_msg.id}"
        
        # Send the link back to the Admin
        await m.reply_text(
            f"✅ **Aapka File Link Taiyar Hai:**\n\n"
            f"📂 **Name:** `{file_name}`\n"
            f"🔗 **Link:** `{share_link}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Share Link 🔗", url=f"https://t.me/share/url?url={share_link}")]
            ])
        )
    except Exception as e:
        # Simple error handling for Flood Waits or admin permission issues
        if "FLOOD_WAIT" in str(e):
            await m.reply_text("⚠️ Telegram limit hit! Thodi der ruk kar files bhejein.")
        else:
            await m.reply_text(f"❌ Error: {e}\n\nCheck karein ki bot channel mein admin hai.")

# --- EXECUTION ---
if __name__ == "__main__":
    # Start the web server for Render keep-alive
    keep_alive()
    print("Dummy server started for Render...")
    
    # Start the Telegram Bot
    print("Bot is starting... No bugs found.")
    bot.run()
