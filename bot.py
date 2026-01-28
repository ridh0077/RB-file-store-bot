import os
import logging
import random
import string
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pymongo import MongoClient
from flask import Flask 
from threading import Thread 

# --- Flask Web Server (Render/Heroku ko online rakhne ke liye) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return "Bot is alive!", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- Basic Logging ---
logging.basicConfig(level=logging.INFO)

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
MONGO_URI = os.environ.get("MONGO_URI")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL")) 
BOT_USERNAME = os.environ.get("BOT_USERNAME") # Aapke bot ka username bina @ ke

# Admin IDs list
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "")
ADMINS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(',') if admin_id]

# --- Database Setup ---
try:
    client = MongoClient(MONGO_URI)
    db = client['file_link_bot']
    files_collection = db['files']
    logging.info("MongoDB Connected Successfully!")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    exit()

# --- Pyrogram Client ---
app = Client("FileLinkBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- Helper Functions ---
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# --- Handlers ---

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    if len(message.command) > 1:
        file_id_str = message.command[1]
        
        # Seedha database se file check karna (No Force Join)
        file_record = files_collection.find_one({"_id": file_id_str})
        if file_record:
            try:
                await client.copy_message(
                    chat_id=message.from_user.id, 
                    from_chat_id=LOG_CHANNEL, 
                    message_id=file_record['message_id']
                )
            except Exception as e:
                await message.reply(f"❌ Error: {e}")
        else:
            await message.reply("🤔 File not found!")
    else:
        await message.reply(f"👋 **Hello {message.from_user.first_name}!**\n\nMai ek File-to-Link bot hu. Mujhe koi bhi file bhejo aur mai link bana dunga.")

# --- Link Generation (Admin Only) ---
@app.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_media(client: Client, message: Message):
    # Admin Restriction
    if message.from_user.id not in ADMINS:
        await message.reply("❌ **Access Denied!**\n\nSirf Admins hi files bhej kar links generate kar sakte hain.")
        return

    # File ko Log Channel mein forward karna
    try:
        log_msg = await message.forward(LOG_CHANNEL)
        file_id_key = generate_random_string()
        
        # Database mein save karna
        files_collection.insert_one({
            "_id": file_id_key,
            "message_id": log_msg.id
        })
        
        # Link generate karna
        share_link = f"https://t.me/{BOT_USERNAME}?start={file_id_key}"
        
        await message.reply(
            f"✅ **Link Generated Successfully!**\n\n**Your Link:** `{share_link}`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Share Link", url=f"https://t.me/share/url?url={share_link}")]])
        )
    except Exception as e:
        await message.reply(f"❌ Error generating link: {e}")

# --- Run Bot ---
if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    app.run()
