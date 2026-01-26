import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- APNI DETAILS YAHAN BHAREIN ---
API_ID = 31567540               
API_HASH = "92b533d7cf66bf9096b738d6fc9a7c3"      
BOT_TOKEN = "8049998572:AAFa833_DlivqwpGMbq4PvK0H1xhTDMYLYU" 
ADMIN_ID = 942084825      
CHANNEL_ID = -1003747593953  

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
@app.on_message(filters.private & (filters.document | filters.video | filters.photo | filters.audio))
async def file_handler(client: Client, message: Message):
    bot_mode = await get_bot_mode()
    if bot_mode == "private" and message.from_user.id not in ADMINS:
        await message.reply("😔 **Sorry!** Abhi sirf Admins hi files upload kar sakte hain.")
        return

    status_msg = await message.reply("⏳ Please wait, file upload kar raha hu...", quote=True)
    
    try:
        forwarded_message = await message.forward(LOG_CHANNEL)
        file_id_str = generate_random_string()
        files_collection.insert_one({'_id': file_id_str, 'message_id': forwarded_message.id})
        bot_username = (await client.get_me()).username
        share_link = f"https://t.me/{bot_username}?start={file_id_str}"
        await status_msg.edit_text(
            f"✅ **Link Generated Successfully!**\n\n🔗 Your Link: `{share_link}`",
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.error(f"File handling error: {e}")
        await status_msg.edit_text(f"❌ **Error!**\n\nKuch galat ho gaya. Please try again.\n`Details: {e}`")

@app.on_message(filters.command("settings") & filters.private)
async def settings_handler(client: Client, message: Message):
    if message.from_user.id not in ADMINS:
        await message.reply("❌ Aapke paas is command ko use karne ki permission nahi hai.")
        return
    
    current_mode = await get_bot_mode()
    
    public_button = InlineKeyboardButton("🌍 Public (Anyone)", callback_data="set_mode_public")
    private_button = InlineKeyboardButton("🔒 Private (Admins Only)", callback_data="set_mode_private")
    keyboard = InlineKeyboardMarkup([[public_button], [private_button]])
    
    await message.reply(
        f"⚙️ **Bot Settings**\n\n"
        f"Abhi bot ka file upload mode **{current_mode.upper()}** hai.\n\n"
        f"**Public:** Koi bhi file bhej kar link bana sakta hai.\n"
        f"**Private:** Sirf admins hi file bhej sakte hain.\n\n"
        f"Naya mode select karein:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^set_mode_"))
async def set_mode_callback(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("Permission Denied!", show_alert=True)
        return
        
    new_mode = callback_query.data.split("_")[2]
    
    settings_collection.update_one(
        {"_id": "bot_mode"},
        {"$set": {"mode": new_mode}},
        upsert=True
    )
    
    await callback_query.answer(f"Mode successfully {new_mode.upper()} par set ho gaya hai!", show_alert=True)
    
    public_button = InlineKeyboardButton("🌍 Public (Anyone)", callback_data="set_mode_public")
    private_button = InlineKeyboardButton("🔒 Private (Admins Only)", callback_data="set_mode_private")
    keyboard = InlineKeyboardMarkup([[public_button], [private_button]])
    
    await callback_query.message.edit_text(
        f"⚙️ **Bot Settings**\n\n"
        f"✅ Bot ka file upload mode ab **{new_mode.upper()}** hai.\n\n"
        f"Naya mode select karein:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex(r"^check_join_"))
async def check_join_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    file_id_str = callback_query.data.split("_", 2)[2]

    if await is_user_member(client, user_id):
        await callback_query.answer("Thanks for joining! File bhej raha hu...", show_alert=True)
        file_record = files_collection.find_one({"_id": file_id_str})
        if file_record:
            try:
                await client.copy_message(chat_id=user_id, from_chat_id=LOG_CHANNEL, message_id=file_record['message_id'])
                await callback_query.message.delete()
            except Exception as e:
                await callback_query.message.edit_text(f"❌ File bhejte waqt error aa gaya.\n`Error: {e}`")
        else:
            await callback_query.message.edit_text("🤔 File not found!")
    else:
        await callback_query.answer("Aapne abhi tak channel join nahi kiya hai. Please join karke dobara try karein.", show_alert=True)

# --- Bot ko Start Karo ---
if __name__ == "__main__":
    if not ADMINS:
        logging.warning("WARNING: ADMIN_IDS is not set. Settings command kaam nahi karega.")
    
    # Flask server ko ek alag thread me start karo
    logging.info("Starting Flask web server...")
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    logging.info("Bot is starting...")
    app.run()
    logging.info("Bot has stopped.")
