import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import asyncio
import json
import tempfile
import time
import re
from flask import Flask, render_template_string

# ==== BOT CONFIGURATION ====
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8420276164:AAE965Rj933Rs7t6fbI7bgGN3-RgapJNzgk")
API_BASE = "https://teradl.tiiny.io/"
ALTERNATE_API = "https://terabox-api.vercel.app/api"
PORT = int(os.environ.get("PORT", 8080))

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
# WEB SERVER FOR RENDER
# =============================
app = Flask(__name__)

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terabox Downloader Bot</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 50px;
                margin: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
            }
            .bot-info {
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: left;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 10px;
                transition: transform 0.3s;
            }
            .feature:hover {
                transform: translateY(-5px);
            }
            .status {
                margin-top: 30px;
                padding: 15px;
                background: rgba(76, 175, 80, 0.3);
                border-radius: 10px;
                font-weight: bold;
            }
            .telegram-link {
                display: inline-block;
                background: #0088cc;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 50px;
                margin-top: 20px;
                font-weight: bold;
                transition: background 0.3s;
            }
            .telegram-link:hover {
                background: #006699;
            }
            code {
                background: rgba(0, 0, 0, 0.3);
                padding: 5px 10px;
                border-radius: 5px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Terabox Downloader Bot</h1>
            <p style="font-size: 1.2em;">Fast and reliable Terabox video downloader Telegram bot</p>
            
            <div class="bot-info">
                <h3>📋 Bot Information</h3>
                <p><strong>Creator:</strong> Genny 🎀</p>
                <p><strong>Channel:</strong> @NetFusionTG</p>
                <p><strong>Status:</strong> <span style="color: #4CAF50;">● Online</span></p>
                <p><strong>Host:</strong> Render Cloud</p>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>📥 Direct Download</h3>
                    <p>Get direct download links for Terabox videos</p>
                </div>
                <div class="feature">
                    <h3>📲 Telegram Download</h3>
                    <p>Videos sent directly in Telegram chat</p>
                </div>
                <div class="feature">
                    <h3>⚡ Fast Processing</h3>
                    <p>Quick download link generation</p>
                </div>
                <div class="feature">
                    <h3>🔒 Secure</h3>
                    <p>Auto-delete original links for privacy</p>
                </div>
            </div>
            
            <div class="status">
                ✅ Bot is running successfully on Render
            </div>
            
            <h3>🚀 How to Use</h3>
            <p>1. Open Telegram and search for the bot</p>
            <p>2. Send command: <code>/genny [terabox_link]</code></p>
            <p>3. Choose your download method</p>
            
            <a href="https://t.me/YOUR_BOT_USERNAME" class="telegram-link" target="_blank">
                ✨ Start Using Bot on Telegram
            </a>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255, 255, 255, 0.2);">
                <p>Made with ❤️ by Genny</p>
                <p>GitHub: Account-Nahi he</p>
            </div>
        </div>
        
        <script>
            // Update status every 30 seconds
            function updateStatus() {
                fetch('/health')
                    .then(response => response.json())
                    .then(data => {
                        if(data.status === 'healthy') {
                            document.querySelector('.status').innerHTML = 
                                '✅ Bot is running successfully on Render';
                            document.querySelector('.status').style.background = 'rgba(76, 175, 80, 0.3)';
                        }
                    })
                    .catch(() => {
                        document.querySelector('.status').innerHTML = 
                            '⚠️ Checking bot status...';
                        document.querySelector('.status').style.background = 'rgba(255, 193, 7, 0.3)';
                    });
            }
            
            // Initial update
            updateStatus();
            
            // Update every 30 seconds
            setInterval(updateStatus, 30000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/health')
def health_check():
    return json.dumps({"status": "healthy", "timestamp": time.time()}), 200, {'Content-Type': 'application/json'}

@app.route('/api/status')
def api_status():
    return json.dumps({
        "bot": "online",
        "sessions": len(user_sessions),
        "timestamp": time.time()
    }), 200, {'Content-Type': 'application/json'}

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
# TELEGRAM BOT FUNCTIONS
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
    
    temp_path = None
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_path = temp_file.name
        
        # Download video with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'video/*',
            'Referer': 'https://www.terabox.com/'
        }
        
        response = requests.get(download_url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 8192
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            # Check file size
            import os
            file_size = os.path.getsize(temp_path)
            size_mb = file_size / (1024 * 1024)
            
            if size_mb > 50:
                await query.message.edit_text(
                    f"⚠️ *File Too Large*\n\n"
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
                
                return
            
            # Upload to Telegram
            await query.message.edit_text(
                f"📤 *Uploading to Telegram...*\n\n"
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
                                f"✅ Downloaded via @TeraboxDownloaderBot\n\n"
                                f"{CREDIT_TEXT}",
                        parse_mode='Markdown',
                        supports_streaming=True
                    )
                
                # Delete processing message
                await query.message.delete()
                
                # Send success message
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ *Video Sent Successfully!*\n\n"
                         f"The video has been sent directly in Telegram.\n\n"
                         f"🔔 *Join:* @NetFusionTG",
                    parse_mode='Markdown'
                )
                
            except Exception as video_error:
                print(f"Video send error: {video_error}")
                await query.message.edit_text(
                    f"❌ *Failed to Send Video*\n\n"
                    f"Please try DIRECT DOWNLOAD option.\n\n"
                    f"{CREDIT_TEXT}",
                    parse_mode='Markdown'
                )
        
        else:
            await query.message.edit_text(
                f"❌ *Download Error*\n\n"
                f"Status: {response.status_code}\n"
                f"Please try DIRECT DOWNLOAD option.\n\n"
                f"{CREDIT_TEXT}",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        print(f"Telegram download error: {e}")
        await query.message.edit_text(
            f"❌ *Error Downloading Video*\n\n"
            f"Please try DIRECT DOWNLOAD option.\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown'
        )
    
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        
        # Clean up session
        if user_id in user_sessions:
            del user_sessions[user_id]

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

{CREDIT_TEXT}
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Bot Error: {context.error}")

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
# MAIN FUNCTION FOR RENDER
# =============================
def run_bot():
    """Run Telegram bot"""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("genny", genny_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("credit", credit_command))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    print("=" * 50)
    print("🤖 TERABOX DOWNLOADER BOT")
    print("=" * 50)
    print(f"🌐 Web Server: http://0.0.0.0:{PORT}")
    print("✅ Bot is running...")
    print("=" * 50)
    
    # Start cleanup task
    asyncio.get_event_loop().create_task(cleanup_old_sessions())
    
    # Start polling
    application.run_polling()

def run_web_server():
    """Run Flask web server"""
    app.run(host='0.0.0.0', port=PORT, debug=False)

def main():
    """Main function to run both bot and web server"""
    import threading
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start web server in main thread
    run_web_server()

# =============================
# RUN FOR RENDER
# =============================
if __name__ == "__main__":
    # Check if running on Render
    if os.environ.get('RENDER', '').lower() == 'true':
        print("🚀 Running on Render Platform")
        print(f"📦 PORT: {PORT}")
        print(f"🔑 BOT_TOKEN: {'Set' if BOT_TOKEN else 'Not Set'}")
        
        # Start both bot and web server
        main()
    else:
        # Run only bot for local testing
        print("🏠 Running locally")
        run_bot()