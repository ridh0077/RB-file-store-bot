import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# --- RENDER KEEP ALIVE LOGIC (Isse error nahi aayega) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive and Running!"

def run_flask():
    # Render default port 8080 use karta hai
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()
# -------------------------------------------------------

# Load variables
load_dotenv()

# Variables (Render Environment Variables se uthayega)
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", -100)) 

bot = Client("RBFileStore", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- EDITABLE CONFIGURATION (Yaha se change kar sakte hain) ---
WELCOME_TEXT = "Hello {name}!\n\nWelcome to my **RBmods channel**.\n\nMain ek file store bot hu. Sirf Admin hi files bhej sakta hai."
BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join RBmods 📢", url="https://t.me/your_channel_link")],
    [InlineKeyboardButton("Support 💬", url="https://t.me/your_username")]
])
# -------------------------------------------------------------

# 1. Start Command
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        text=WELCOME_TEXT.format(name=message.from_user.first_name),
        reply_markup=BUTTONS
    )

# 2. File Forwarding (Sirf Admin ke liye)
@bot.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def handle_files(client, message):
    # Security: Check if user is Admin
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ Aap admin nahi hain! Sirf admin hi yaha files bhej sakta hai.")
        return

    # Agar Admin hai toh Log Channel me forward karega
    try:
        await message.forward(LOG_CHANNEL)
        await message.reply_text("✅ File successfully saved in Log Channel!")
    except Exception as e:
        await message.reply_text(f"❌ Error: Log Channel check karein. {e}")

# 3. Text Message Restriction (Koi aur message na kar paye)
@bot.on_message(filters.private & filters.text & ~filters.command("start"))
async def restrict_chat(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("⚠️ Sorry! Sirf Admin hi is bot se baat kar sakta hai.")
    else:
        await message.reply_text("Hello Admin! Main aapke commands ka wait kar raha hoon.")

# Bot Start karne ka tarika
if __name__ == "__main__":
    print("Starting Web Server...")
    keep_alive()  # Isse Render ka 'No Open Ports' error fix ho jayega
    print("Bot is running...")
    bot.run()
