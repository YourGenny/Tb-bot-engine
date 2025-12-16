import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import asyncio
import json
import os
import tempfile
import time
import re

# ==== BOT CONFIGURATION ====
BOT_TOKEN = "8420276164:AAE965Rj933Rs7t6fbI7bgGN3-RgapJNzgk"
API_BASE = "https://teradl.tiiny.io/"
ALTERNATE_API = "https://terabox-api.vercel.app/api"

# ==== CREDIT INFORMATION ====
CREDIT_TEXT = """
╔══════════════════════╗
║     🤖 BOT CREDITS           ║
╠══════════════════════╣
║ • Creator: 𝗚𝗲𝗻𝗻𝘆 🎀         ║
║ • Channel: @NetFusionTG     ║
║ • GitHub: Account-Nahi he   ║
╚══════════════════════╝
"""

# User data storage
user_sessions = {}

# =============================
# /start COMMAND
# =============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = f"""
🎯 *Welcome to Terabox Downloader Bot* 🎯

Use command:
• /genny [link] - For download generation

✨ *Features:*
• Direct Download - Get download link
• Telegram Download - Video sent directly in Telegram
• Fast processing
• Free to use

{CREDIT_TEXT}

📌 *How to use:* Use /genny command with Terabox link!
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# =============================
# GET DOWNLOAD LINK FROM MULTIPLE APIS
# =============================
def get_download_link_from_apis(user_link):
    """Try multiple APIs to get download link"""
    
    # Try Primary API
    try:
        api_url = f"{API_BASE}?key=RushVx&link={user_link}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.terabox.com/'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Try to extract URL from response
            content = response.text
            
            # Check if response is JSON
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                        item = data["data"][0]
                        if "download" in item:
                            return item["download"], item.get("title", "Video"), item.get("size", "Unknown")
                    elif "download_url" in data:
                        return data["download_url"], data.get("title", "Video"), data.get("size", "Unknown")
            except json.JSONDecodeError:
                pass
            
            # Search for URLs in text response
            url_patterns = [
                r'https://[a-zA-Z0-9._/-]+\.mp4(?:\?[^\s"]*)?',
                r'https://d\d+\.terabox\.com/[^\s"]+',
                r'https://[a-zA-Z0-9._/-]+nephobox\.com/[^\s"]+',
                r'https://[a-zA-Z0-9._/-]+1024tera\.com/[^\s"]+'
            ]
            
            for pattern in url_patterns:
                match = re.search(pattern, content)
                if match:
                    url = match.group(0)
                    if len(url) > 20:
                        return url, "Video", "Unknown"
    except Exception as e:
        print(f"Primary API error: {e}")
    
    # Try Alternate API
    try:
        alt_api_url = f"{ALTERNATE_API}?url={user_link}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(alt_api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                if "direct_link" in data:
                    return data["direct_link"], data.get("filename", "Video"), data.get("size", "Unknown")
                elif "url" in data:
                    return data["url"], data.get("filename", "Video"), data.get("size", "Unknown")
    except Exception as e:
        print(f"Alternate API error: {e}")
    
    # Try Third API (Fallback)
    try:
        third_api = f"https://tb-api.suprfi.repl.co/api?url={user_link}"
        response = requests.get(third_api, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "downloadUrl" in data:
                return data["downloadUrl"], data.get("fileName", "Video"), data.get("fileSize", "Unknown")
    except:
        pass
    
    return None, "Video", "Unknown"

# =============================
# /genny COMMAND
# =============================
async def genny_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📝 *Usage:* `/genny [terabox_link]`\n\n"
            "Example: `/genny https://terabox.com/s/abc123`",
            parse_mode='Markdown'
        )
        return
    
    user_link = ' '.join(context.args)
    user_id = update.effective_user.id
    message_id = update.message.message_id
    chat_id = update.message.chat_id
    
    # Validate link
    if not user_link.startswith(('http://', 'https://')):
        await update.message.reply_text(
            "❌ *Invalid Link*\n\n"
            "Please send a valid URL starting with http:// or https://",
            parse_mode='Markdown'
        )
        return
    
    # Check if it's a Terabox link
    if 'terabox.com' not in user_link and '1024tera.com' not in user_link:
        await update.message.reply_text(
            "❌ *Not a Terabox Link*\n\n"
            "Please send a valid Terabox link.",
            parse_mode='Markdown'
        )
        return
    
    # Store user session
    user_sessions[user_id] = {
        "link": user_link,
        "message_id": message_id,
        "chat_id": chat_id,
        "timestamp": time.time()
    }
    
    # Show processing message
    processing_msg = await update.message.reply_text(
        f"🔍 *Processing Your Link...*\n\n"
        f"📎 Link: `{user_link[:50]}...`\n\n"
        f"⏳ Getting download information...\n\n"
        f"{CREDIT_TEXT}",
        parse_mode='Markdown'
    )
    
    user_sessions[user_id]["processing_msg_id"] = processing_msg.message_id
    
    # Get download link from APIs
    download_url, title, size = get_download_link_from_apis(user_link)
    
    if download_url:
        # Store download info in session
        user_sessions[user_id].update({
            "download_url": download_url,
            "title": title,
            "size": size
        })
        
        # Delete processing message
        await processing_msg.delete()
        
        # Show two buttons
        keyboard = [
            [
                InlineKeyboardButton("📥 GET DOWNLOAD LINK", callback_data=f"direct_{user_id}"),
                InlineKeyboardButton("📲 DIRECT TELEGRAM", callback_data=f"telegram_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        button_msg = await update.message.reply_text(
            f"✅ *Download Options Ready!*\n\n"
            f"📁 *Title:* `{title}`\n"
            f"📊 *Size:* `{size}`\n\n"
            f"*Choose your download method:*\n\n"
            f"1️⃣ *📥 DIRECT DOWNLOAD* - Get download link\n"
            f"2️⃣ *📲 TELEGRAM DOWNLOAD* - Video sent directly in Telegram\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        user_sessions[user_id]["button_msg_id"] = button_msg.message_id
        
    else:
        await processing_msg.edit_text(
            f"❌ *Could Not Get Download Link*\n\n"
            f"Unable to fetch download information for this link.\n\n"
            f"*Possible reasons:*\n"
            f"• Link is private/restricted\n"
            f"• Video has been removed\n"
            f"• Server issue\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown'
        )
        del user_sessions[user_id]
    
    # Auto-delete original message after 3 seconds
    await asyncio.sleep(3)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

# =============================
# BUTTON CALLBACK HANDLER
# =============================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data.startswith("direct_"):
        user_id = int(callback_data.split("_")[1])
        await handle_direct_download(query, context, user_id)
    
    elif callback_data.startswith("telegram_"):
        user_id = int(callback_data.split("_")[1])
        await handle_telegram_download(query, context, user_id)

# =============================
# HANDLE DIRECT DOWNLOAD
# =============================
async def handle_direct_download(query, context, user_id):
    """Handle direct download button click"""
    if user_id not in user_sessions:
        await query.message.edit_text("⚠️ *Session expired*\n\nPlease use /genny command again.", parse_mode='Markdown')
        return
    
    user_data = user_sessions[user_id]
    
    if "download_url" not in user_data:
        await query.message.edit_text("❌ *No download link available*\n\nPlease try again.", parse_mode='Markdown')
        return
    
    download_url = user_data["download_url"]
    title = user_data.get("title", "Video")
    size = user_data.get("size", "Unknown")
    
    # Create direct download button
    keyboard = [[InlineKeyboardButton("📥 CLICK TO DOWNLOAD", url=download_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        f"✅ *Direct Download Link Ready!*\n\n"
        f"📁 *Title:* `{title}`\n"
        f"📊 *Size:* `{size}`\n\n"
        f"Click the button below to download:\n\n"
        f"{CREDIT_TEXT}",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    # Clean up session
    if user_id in user_sessions:
        del user_sessions[user_id]

# =============================
# HANDLE TELEGRAM DOWNLOAD
# =============================
async def handle_telegram_download(query, context, user_id):
    """Handle telegram download button click"""
    if user_id not in user_sessions:
        await query.message.edit_text("⚠️ *Session expired*\n\nPlease use /genny command again.", parse_mode='Markdown')
        return
    
    user_data = user_sessions[user_id]
    
    if "download_url" not in user_data:
        await query.message.edit_text("❌ *No download link available*\n\nPlease try Direct Download option.", parse_mode='Markdown')
        return
    
    download_url = user_data["download_url"]
    title = user_data.get("title", "Video")
    size = user_data.get("size", "Unknown")
    chat_id = user_data["chat_id"]
    
    # Update message to show downloading
    await query.message.edit_text(
        f"⏬ *Starting Telegram Download...*\n\n"
        f"📁 *Title:* `{title}`\n"
        f"📊 *Size:* `{size}`\n\n"
        f"⏳ Preparing to download...\n\n"
        f"{CREDIT_TEXT}",
        parse_mode='Markdown'
    )
    
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
        
        # Download video with proper headers to avoid 403
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Range': 'bytes=0-',
            'Referer': 'https://www.terabox.com/',
            'Origin': 'https://www.terabox.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site'
        }
        
        await query.message.edit_text(
            f"⏬ *Downloading Video...*\n\n"
            f"📁 *Title:* `{title}`\n"
            f"📊 *Connecting to server...*\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown'
        )
        
        # Try to download with session to handle cookies
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(download_url, stream=True, timeout=30)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        if total_size > 0 and downloaded % (5 * 1024 * 1024) < chunk_size:
                            percent = min(99, int((downloaded / total_size) * 100))
                            await query.message.edit_text(
                                f"⏬ *Downloading... {percent}%*\n\n"
                                f"📁 *Title:* `{title}`\n"
                                f"📊 *Progress:* {downloaded//1024//1024}MB/{total_size//1024//1024}MB\n\n"
                                f"{CREDIT_TEXT}",
                                parse_mode='Markdown'
                            )
            
            # Check file size
            file_size = os.path.getsize(temp_path)
            size_mb = file_size / (1024 * 1024)
            
            if size_mb < 1:
                await query.message.edit_text(
                    f"❌ *Download Failed*\n\n"
                    f"Downloaded file is too small ({size_mb:.2f}MB).\n"
                    f"Please try Direct Download option.\n\n"
                    f"{CREDIT_TEXT}",
                    parse_mode='Markdown'
                )
                os.remove(temp_path)
                return
            
            # Check if file is too large
            if size_mb > 200:
                await query.message.edit_text(
                    f"⚠️ *File Too Large*\n\n"
                    f"📁 *Title:* `{title}`\n"
                    f"📊 *Size:* {size_mb:.1f}MB\n\n"
                    f"File is too large for Telegram. Use Direct Download.\n\n"
                    f"{CREDIT_TEXT}",
                    parse_mode='Markdown'
                )
                
                # Offer direct download
                keyboard = [[InlineKeyboardButton("📥 DIRECT DOWNLOAD", url=download_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🔗 *Direct Download Link*\n\nFile is too large for Telegram.",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
                os.remove(temp_path)
                return
            
            # Upload to Telegram
            await query.message.edit_text(
                f"📤 *Uploading to Telegram...*\n\n"
                f"📁 *Title:* `{title}`\n"
                f"📊 *Size:* {size_mb:.1f}MB\n\n"
                f"⏳ Please wait...\n\n"
                f"{CREDIT_TEXT}",
                parse_mode='Markdown'
            )
            
            # Try to send as video
            try:
                with open(temp_path, 'rb') as video_file:
                    await context.bot.send_video(
                        chat_id=chat_id,
                        video=video_file,
                        caption=f"🎬 *{title}*\n\n"
                                f"📊 Size: {size_mb:.1f}MB\n"
                                f"✅ Downloaded via @TeraboxDownloaderBot\n\n"
                                f"{CREDIT_TEXT}",
                        parse_mode='Markdown',
                        supports_streaming=True,
                        read_timeout=60,
                        write_timeout=60,
                        connect_timeout=60
                    )
                
                # Delete processing message
                await query.message.delete()
                
                # Send success message
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ *Video Sent Successfully!*\n\n"
                         f"The video has been sent directly in Telegram.\n\n"
                         f"🔔 *Join:* @NetFusionTG\n"
                         f"✨ Thanks for using our service!",
                    parse_mode='Markdown'
                )
                
            except Exception as video_error:
                print(f"Video send error: {video_error}")
                
                # Try as document
                try:
                    with open(temp_path, 'rb') as doc_file:
                        await context.bot.send_document(
                            chat_id=chat_id,
                            document=doc_file,
                            caption=f"📁 *{title}*\n\n"
                                    f"📊 Size: {size_mb:.1f}MB\n"
                                    f"✅ Sent as document\n\n"
                                    f"{CREDIT_TEXT}",
                            parse_mode='Markdown'
                        )
                    
                    await query.message.delete()
                    
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"✅ *File Sent as Document!*\n\n"
                             f"The video was sent as a document file.",
                        parse_mode='Markdown'
                    )
                    
                except Exception as doc_error:
                    print(f"Document send error: {doc_error}")
                    await query.message.edit_text(
                        f"❌ *Failed to Send File*\n\n"
                        f"Error: {str(doc_error)[:100]}\n\n"
                        f"Please try DIRECT DOWNLOAD option.\n\n"
                        f"{CREDIT_TEXT}",
                        parse_mode='Markdown'
                    )
        
        else:
            # Handle 403 and other errors
            error_msg = f"Download failed with status {response.status_code}"
            if response.status_code == 403:
                error_msg = "Access forbidden (403). The server denied the download request."
            elif response.status_code == 404:
                error_msg = "File not found (404). The video may have been removed."
            
            await query.message.edit_text(
                f"❌ *Download Error*\n\n"
                f"{error_msg}\n\n"
                f"Please try DIRECT DOWNLOAD option.\n\n"
                f"{CREDIT_TEXT}",
                parse_mode='Markdown'
            )
    
    except requests.exceptions.Timeout:
        await query.message.edit_text(
            f"❌ *Timeout Error*\n\n"
            f"The download took too long.\n"
            f"Please try DIRECT DOWNLOAD option.\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown'
        )
    
    except Exception as e:
        print(f"Telegram download error: {e}")
        await query.message.edit_text(
            f"❌ *Error Downloading Video*\n\n"
            f"Error: {str(e)[:100]}\n\n"
            f"Please try DIRECT DOWNLOAD option.\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown'
        )
    
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        
        # Clean up session
        if user_id in user_sessions:
            del user_sessions[user_id]

# =============================
# OTHER COMMANDS
# =============================
async def credit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(CREDIT_TEXT, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
📖 *HELP GUIDE*

*Available Commands:*
/start - Start the bot
/genny [link] - Download Terabox video
/help - Show this help
/credit - Show bot credits

*How to Use:*
1. Send `/genny [terabox_link]`
2. Bot fetches download information
3. Choose download method:
   • 📥 DIRECT DOWNLOAD - Get download link
   • 📲 TELEGRAM DOWNLOAD - Video sent directly in Telegram

*Features:*
• Multiple API fallbacks
• Progress updates
• File size checking
• Auto-delete original links

*Note:* Some videos may have restrictions that prevent downloading.

{CREDIT_TEXT}
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# =============================
# CLEANUP OLD SESSIONS
# =============================
async def cleanup_old_sessions():
    """Clean up old user sessions periodically"""
    while True:
        await asyncio.sleep(300)
        current_time = time.time()
        expired_users = []
        
        for user_id, session in list(user_sessions.items()):
            if current_time - session.get('timestamp', 0) > 600:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del user_sessions[user_id]
        
        if expired_users:
            print(f"✅ Cleaned {len(expired_users)} expired sessions")

# =============================
# ERROR HANDLER
# =============================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Bot Error: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                f"⚠️ *Bot Error*\n\n"
                f"An error occurred. Please try again.\n\n"
                f"Error: `{str(context.error)[:100]}`",
                parse_mode='Markdown'
            )
    except:
        pass

# =============================
# MAIN FUNCTION
# =============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("genny", genny_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("credit", credit_command))
    
    # Add callback query handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start cleanup task
    asyncio.get_event_loop().create_task(cleanup_old_sessions())
    
    print("=" * 50)
    print("🤖 TERABOX DOWNLOADER BOT")
    print("=" * 50)
    print("✅ Fixed 403 Error")
    print("✅ Multiple API Support")
    print("✅ Direct Download Button")
    print("✅ Telegram Download Button")
    print("✅ Better Error Handling")
    print("=" * 50)
    print("Bot is running...")
    
    app.run_polling()

# =============================
# RUN BOT
# =============================
if __name__ == "__main__":
    main()