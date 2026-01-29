import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Client("my_file_store_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- EDITABLE MESSAGES ---
WELCOME_TEXT = "Hello {name}!\n\nWelcome to my **RBmods channel** bot. Aapka swagat hai!"
START_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("Join Channel 📢", url="https://t.me/your_channel_link")],
    [InlineKeyboardButton("Support 💬", url="https://t.me/your_username")]
])
# -------------------------

# Start Command
@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    name = message.from_user.first_name
    await message.reply_text(
        text=WELCOME_TEXT.format(name=name),
        reply_markup=START_BUTTONS
    )

# File Forwarding Logic (Only for Admin)
@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def forward_handler(client, message):
    # Security Check: Sirf Admin hi file bhej sakta hai
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ Sorry! Aap is bot ke admin nahi hain. Aap messages forward nahi kar sakte.")
        return

    # Admin ke liye file handling
    await message.reply_text("✅ File Received! Ab aap isse forward kar sakte hain ya link generate kar sakte hain.")
    # Agar aapko file store karni hai toh yaha channel forwarding ka code add ho sakta hai.

# Chat Restriction (Taaki koi aur message na kare)
@bot.on_message(filters.private & filters.text & ~filters.command("start"))
async def restricted_handler(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("⚠️ Sirf Admin hi yaha message kar sakta hai.")
    else:
        await message.reply_text("Hello Admin! Main aapke order ka wait kar raha hu.")

print("Bot is starting...")
bot.run()
