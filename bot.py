import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# --- RENDER KEEP ALIVE (Server setup) ---
app = Flask('')
@app.route('/')
def home():
    return "RBmods Bot is Active!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()
# ----------------------------------------

load_dotenv()

# Basic Variables
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

bot = Client("RBFileBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- AAP ISE EDIT KAR SAKTE HAIN ---
WELCOME_MSG = "Hello {name}!\n\nWelcome to my **RBmods channel**.\n\nAapka swagat hai hamare bot mein!"
START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join RBmods 📢", url="https://t.me/RBmods")],
    [InlineKeyboardButton("Owner 👤", url="https://t.me/your_username")]
])
# ----------------------------------

# 1. Start Command (Sabke liye)
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    name = message.from_user.first_name
    await message.reply_text(
        text=WELCOME_MSG.format(name=name),
        reply_markup=START_BUTTONS
    )

# 2. Files handling (Sirf Admin ke liye - Bina Log Channel ke)
@bot.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def file_handler(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ Sirf Admin hi yaha file bhej sakta hai.")
        return
    
    # Ab bot sirf file receive karega, log channel ka error nahi aayega
    await message.reply_text("✅ Admin, file receive ho gayi hai! Ab aap ise kahin bhi forward kar sakte hain.")

# 3. Message Handling (Security Check)
@bot.on_message(filters.private & filters.text & ~filters.command("start"))
async def text_handler(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("⚠️ Ye bot sirf Admin ke use ke liye hai.")
    else:
        await message.reply_text(f"Hello Admin, aapne kaha: {message.text}")

if __name__ == "__main__":
    keep_alive()
    print("Bot is starting without Log Channel...")
    bot.run()
