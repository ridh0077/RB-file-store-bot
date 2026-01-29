import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load variables
load_dotenv()

# Variables with safe defaults to avoid 'NoneType' error
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))
# Yaha error fix kiya gaya hai (default -100 diya hai taaki crash na ho)
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", -100)) 

bot = Client("RBFileStore", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- CONFIGURATION ---
WELCOME_TEXT = "Hello {name}!\n\nWelcome to my **RBmods channel**.\n\nMain ek file store bot hu. Sirf Admin hi files bhej sakta hai."
JOIN_BUTTON = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join RBmods 📢", url="https://t.me/your_channel_link")]
])

# Start Command
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        text=WELCOME_TEXT.format(name=message.from_user.first_name),
        reply_markup=JOIN_BUTTON
    )

# File Forwarding (Strictly Admin Only)
@bot.on_message(filters.private & (filters.document | filters.video | filters.photo))
async def handle_files(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ Aap admin nahi hain! Sirf @your_username hi files bhej sakta hai.")
        return

    # Forwarding to Log Channel
    try:
        await message.forward(LOG_CHANNEL)
        await message.reply_text("✅ File successfully saved in Log Channel!")
    except Exception as e:
        await message.reply_text(f"❌ Error: Log Channel setup nahi hai sahi se. {e}")

# Restrict normal text messages for others
@bot.on_message(filters.private & filters.text & ~filters.command("start"))
async def restrict_chat(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("⚠️ Ye bot sirf Admin ke liye hai.")

print("Bot is running...")
bot.run()
