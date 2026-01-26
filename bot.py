import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- APNI DETAILS YAHAN BHAREIN ---
API_ID = 31567540               
API_HASH = "92b533d7cf66bf9096b738d6fc9a7c3"      
BOT_TOKEN = "8350076863:AAGmoDb8NCL1PXmrnd3hDiLYEeWK6bYG7no" 
ADMIN_ID = 942084825      
CHANNEL_ID = -1003622282918  

app = Client("file_share_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Database setup (Files yaad rakhne ke liye)
db = sqlite3.connect("files_data.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS my_files (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg_id INTEGER)")
db.commit()

# 1. Admin File Upload Logic
@app.on_message((filters.document | filters.video | filters.audio | filters.photo) & filters.user(ADMIN_ID))
async def store_file(client, message):
    sent_msg = await message.forward(chat_id=CHANNEL_ID)
    
    # File name nikalna
    f_name = "Media File"
    if message.document: f_name = message.document.file_name
    elif message.video: f_name = "Video File"
    
    # DB mein save karein
    cursor.execute("INSERT INTO my_files (name, msg_id) VALUES (?, ?)", (f_name, sent_msg.id))
    db.commit()

    share_link = f"https://t.me/{app.me.username}?start={sent_msg.id}"
    await message.reply_text(
        f"✅ **Owner Sahab, Link Taiyar Hai!**\n\nFile: {f_name}\nLink: `{share_link}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share Karein 🚀", url=f"https://telegram.me/share/url?url={share_link}")]])
    )

# 2. File List nikalne ka logic
async def get_file_list():
    cursor.execute("SELECT name, msg_id FROM my_files ORDER BY id DESC LIMIT 15")
    rows = cursor.fetchall()
    if not rows:
        return "Owner Sahab, abhi koi file nahi hai."
    
    text = "📂 **Aapki Recent Files:**\n\n"
    for name, m_id in rows:
        link = f"https://t.me/{app.me.username}?start={m_id}"
        text += f"📄 `{name}`\n🔗 `{link}`\n\n"
    return text

# 3. Start Command with Admin Button
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    if len(message.command) > 1:
        msg_id = int(message.command[1])
        try:
            await client.copy_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=msg_id)
        except:
            await message.reply_text("❌ File nahi mili!")
    else:
        buttons = []
        if message.from_user.id == ADMIN_ID:
            buttons.append([InlineKeyboardButton("📂 My Files List", callback_data="show_list")])
        
        await message.reply_text(
            f"Hello {message.from_user.mention}!\nMain aapka Private File Share Bot hoon.",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )

# Button click handle karna
@app.on_callback_query(filters.regex("show_list"))
async def cb_handler(client, query):
    file_list_text = await get_file_list()
    await query.message.edit_text(file_list_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]))

@app.on_callback_query(filters.regex("back_start"))
async def back_handler(client, query):
    await start_command(client, query.message)

print("⚡ Bot List Button ke saath Start ho gaya hai!")
app.run()
