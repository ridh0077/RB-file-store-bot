import os
import threading
import asyncio
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, RPCError, PeerIdInvalid
from dotenv import load_dotenv

# --- RENDER KEEP ALIVE SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "RBmods Pro Bot is Live!"

def run_flask():
    try:
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
    except Exception as e:
        print(f"Flask Error: {e}")

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- BOT CONFIGURATION ---
load_dotenv()

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

# Smart Log Channel Fixer
def get_log_id():
    raw_id = str(os.environ.get("LOG_CHANNEL", "0")).strip()
    if not raw_id or raw_id == "0": return 0
    if raw_id.startswith("-100"): return int(raw_id)
    return int("-100" + raw_id) if raw_id.isdigit() else int(raw_id)

LOG_CHANNEL = get_log_id()

bot = Client("RBFileStore", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- PEER RESOLVER FUNCTION ---
# Ye function bot ko majboor karega channel pehchanne ke liye
async def resolve_peer(c):
    try:
        await c.get_chat(LOG_CHANNEL)
        return True
    except Exception as e:
        print(f"Peer Resolution Error: {e}")
        return False

# --- COMMANDS & HANDLERS ---

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    if len(m.command) > 1:
        file_id = m.command[1]
        
        if LOG_CHANNEL == 0:
            return await m.reply_text("❌ LOG_CHANNEL Configured nahi hai.")

        try:
            # Forcefully resolve peer before copying
            await c.get_chat(LOG_CHANNEL)
            
            await c.copy_message(
                chat_id=m.from_user.id, 
                from_chat_id=LOG_CHANNEL, 
                message_id=int(file_id)
            )
        except PeerIdInvalid:
            await m.reply_text(f"❌ Error: Bot channel ko pehchan nahi raha.\n\n**Solution:** Storage channel mein bot ko nikal kar phir se add karein aur Admin banayein.")
        except Exception as e:
            await m.reply_text(f"❌ Error: File nahi mili.\n`Detail: {str(e)}`")
        return

    await m.reply_text(
        text=f"Hello {m.from_user.first_name}!\n\nWelcome to **RBmods File Store**. Send me any file to get a link.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel 📢", url="https://t.me/rbmodschats")]])
    )

@bot.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def gen_link(c, m):
    if m.from_user.id != ADMIN_ID:
        return

    if LOG_CHANNEL == 0:
        return await m.reply_text("❌ LOG_CHANNEL ID missing hai.")

    try:
        # Step 1: Force resolve the channel
        await c.get_chat(LOG_CHANNEL)
        
        # Step 2: Copy file to Storage
        log_msg = await m.copy(LOG_CHANNEL)
        
        # Step 3: Generate Link
        me = await c.get_me()
        share_link = f"https://t.me/{me.username}?start={log_msg.id}"
        
        file_name = m.document.file_name if m.document else "File"
        
        await m.reply_text(
            f"✅ **Link Generated!**\n\n📂 **Name:** `{file_name}`\n🔗 **Link:** `{share_link}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share Link 🔗", url=f"https://t.me/share/url?url={share_link}")]])
        )
    except Exception as e:
        await m.reply_text(f"❌ Error: {str(e)}\n\n**Pakka Check Karein:** Kya bot is ID `{LOG_CHANNEL}` wale channel mein Admin hai?")

# --- STARTUP ---
if __name__ == "__main__":
    keep_alive()
    print(f"Bot starting with Log ID: {LOG_CHANNEL}")
    bot.run()