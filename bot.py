import os
import threading
import asyncio
import time
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, FloodWait, RPCError
from dotenv import load_dotenv

# --- RENDER KEEP ALIVE SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "RBmods Pro File Store Bot is Active!"

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

# Smart Log Channel Fix
def format_id(id_val):
    val = str(id_val).strip()
    if not val or val == "0": return 0
    if val.startswith("-100"): return int(val)
    return int("-100" + val) if val.isdigit() else int(val)

LOG_CHANNEL = format_id(os.environ.get("LOG_CHANNEL", "0"))
# Force Join Channel (Optional: Environment var mein AUTH_CHANNEL daalein)
AUTH_CHANNEL = format_id(os.environ.get("AUTH_CHANNEL", "0"))

bot = Client("RBFileStorePro", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Temporary database for users (In-memory for safety)
# Note: Render par restart hone par users reset honge, permanent ke liye MongoDB chahiye hota hai.
users_list = set()

# Messages
START_MSG = "Hello {name}!\n\nWelcome to **RBmods Pro File Store**.\n\nMain aapki files ko safe rakhta hoon aur unka shareable link banata hoon. Niche diye buttons ka use karein."
ABOUT_MSG = "📂 **Bot Name:** RBmods File Store\n💻 **Developer:** @RBmods\n📜 **Language:** Python (Pyrogram)\n🛰 **Server:** Render"

# Buttons
MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join Channel 📢", url="https://t.me/rbmodschats")],
    [InlineKeyboardButton("Support / Help 💬", url="https://t.me/rbmodschats")]
])

# --- HELPER FUNCTIONS ---

async def check_fsub(c, m):
    if not AUTH_CHANNEL or AUTH_CHANNEL == 0:
        return True
    try:
        await c.get_chat_member(AUTH_CHANNEL, m.from_user.id)
        return True
    except UserNotParticipant:
        try:
            invite = await c.export_chat_invite_link(AUTH_CHANNEL)
        except:
            invite = "https://t.me/rbmodschats"
        
        await m.reply_text(
            text="❌ **Access Denied!**\n\nLink lene ke liye aapko hamare channel join karna padega.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Join Channel 📢", url=invite)],
                [InlineKeyboardButton("Try Again 🔄", url=f"https://t.me/{(await c.get_me()).username}?start={m.command[1] if len(m.command) > 1 else ''}")]
            ])
        )
        return False
    except Exception:
        return True

# --- HANDLERS ---

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(c, m):
    # Add user to list
    users_list.add(m.from_user.id)
    
    # Check Force Join
    if not await check_fsub(c, m):
        return

    # Handle Link
    if len(m.command) > 1:
        file_id = m.command[1]
        if LOG_CHANNEL == 0:
            return await m.reply_text("❌ Error: LOG_CHANNEL set nahi hai.")
        
        try:
            msg = await c.copy_message(
                chat_id=m.from_user.id, 
                from_chat_id=LOG_CHANNEL, 
                message_id=int(file_id)
            )
            # Auto delete message logic (optional) can be added here
        except Exception as e:
            await m.reply_text(f"❌ Error: File nahi mili.\n`Detail: {e}`")
        return

    # Normal Start
    await m.reply_text(
        text=START_MSG.format(name=m.from_user.first_name),
        reply_markup=MAIN_BUTTONS
    )

@bot.on_message(filters.command("about") & filters.private)
async def about_handler(c, m):
    await m.reply_text(ABOUT_MSG)

# --- ADMIN COMMANDS ---

@bot.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats_handler(c, m):
    count = await c.get_chat_history_count(LOG_CHANNEL) if LOG_CHANNEL != 0 else 0
    await m.reply_text(f"📊 **Bot Statistics:**\n\n👥 **Total Users (Session):** `{len(users_list)}` \n📂 **Total Files Stored:** `{count}`\n📍 **Log ID:** `{LOG_CHANNEL}`")

@bot.on_message(filters.command("broadcast") & filters.user(ADMIN_ID) & filters.reply)
async def broadcast_handler(c, m):
    msg = m.reply_to_message
    sent = 0
    await m.reply_text("📢 Broadcast shuru ho raha hai...")
    for user in list(users_list):
        try:
            await msg.copy(user)
            sent += 1
            await asyncio.sleep(0.3) # Flood wait se bachne ke liye
        except:
            pass
    await m.reply_text(f"✅ Broadcast khatam! `{sent}` users ko message mil gaya.")

# --- FILE TO LINK GENERATOR ---

@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def file_link_gen(c, m):
    if m.from_user.id != ADMIN_ID:
        return

    if LOG_CHANNEL == 0:
        return await m.reply_text("❌ LOG_CHANNEL configure karein link banane ke liye.")

    try:
        # File info
        file_name = "File"
        if m.document: file_name = m.document.file_name
        elif m.video: file_name = m.video.file_name or "Video"
        
        # Store in Log Channel
        log_msg = await m.copy(LOG_CHANNEL)
        bot_info = await c.get_me()
        share_link = f"https://t.me/{bot_info.username}?start={log_msg.id}"
        
        await m.reply_text(
            f"✅ **Link Generated!**\n\n📂 **Name:** `{file_name}`\n🔗 **Link:** `{share_link}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Share Link 🔗", url=f"https://t.me/share/url?url={share_link}")]
            ])
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}\n\nCheck karein ki bot Storage Channel mein **Admin** hai.")

# --- STARTUP ---

if __name__ == "__main__":
    keep_alive()
    print("RBmods Pro Bot is initializing...")
    if LOG_CHANNEL == 0:
        print("WARNING: LOG_CHANNEL ID is missing or invalid!")
    else:
        print(f"Connected to Log Channel: {LOG_CHANNEL}")
    
    bot.run()