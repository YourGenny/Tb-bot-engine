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
PORT = int(os.environ.get("PORT", 10000))

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
        <meta charset="UTF-8">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #fff;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                width: 100%;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            @media (max-width: 900px) {
                .container {
                    grid-template-columns: 1fr;
                }
            }
            
            .left-side {
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            
            .right-side {
                display: flex;
                flex-direction: column;
                gap: 25px;
            }
            
            .logo {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .logo h1 {
                font-size: 3em;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #fff, #f0f0f0);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            
            .logo p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .bot-stats {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
            }
            
            .stat-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .stat-item:last-child {
                border-bottom: none;
            }
            
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 10px;
            }
            
            .status-online {
                background: #4CAF50;
                box-shadow: 0 0 10px #4CAF50;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin: 30px 0;
            }
            
            .feature-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .feature-card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.2);
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            }
            
            .feature-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
            }
            
            .how-to-use {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 25px;
            }
            
            .step {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .step:last-child {
                margin-bottom: 0;
                padding-bottom: 0;
                border-bottom: none;
            }
            
            .step-number {
                background: linear-gradient(45deg, #667eea, #764ba2);
                width: 40px;
                height: 40px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                font-size: 1.2em;
                margin-right: 20px;
                flex-shrink: 0;
            }
            
            .telegram-btn {
                display: inline-block;
                background: linear-gradient(45deg, #0088cc, #006699);
                color: white;
                padding: 18px 40px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                font-size: 1.2em;
                text-align: center;
                margin-top: 20px;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(0, 136, 204, 0.4);
            }
            
            .telegram-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(0, 136, 204, 0.6);
            }
            
            .command-box {
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                margin: 10px 0;
                border-left: 4px solid #667eea;
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.2);
                opacity: 0.8;
            }
            
            .heart {
                color: #ff4757;
                animation: heartbeat 1.5s infinite;
            }
            
            @keyframes heartbeat {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            .update-time {
                font-size: 0.9em;
                opacity: 0.7;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="left-side">
                <div class="logo">
                    <h1>🤖 Terabox Downloader</h1>
                    <p>Fast & Reliable Terabox Video Downloader Bot</p>
                </div>
                
                <div class="bot-stats">
                    <div class="stat-item">
                        <span>Bot Status:</span>
                        <span><span class="status-indicator status-online"></span> Online</span>
                    </div>
                    <div class="stat-item">
                        <span>Active Sessions:</span>
                        <span id="sessionCount">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Host Platform:</span>
                        <span>Render Cloud</span>
                    </div>
                    <div class="stat-item">
                        <span>Uptime:</span>
                        <span id="uptime">Just started</span>
                    </div>
                </div>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">📥</div>
                        <h3>Direct Download</h3>
                        <p>Get instant download links</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📲</div>
                        <h3>Telegram Download</h3>
                        <p>Videos sent directly in chat</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h3>Fast Processing</h3>
                        <p>Quick download generation</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔒</div>
                        <h3>Secure</h3>
                        <p>Auto-delete for privacy</p>
                    </div>
                </div>
                
                <a href="https://t.me/terabox_download_genny_bot" class="telegram-btn" target="_blank">
                    🚀 Start Using Bot
                </a>
            </div>
            
            <div class="right-side">
                <div class="how-to-use">
                    <h2 style="margin-bottom: 25px; text-align: center;">📖 How to Use</h2>
                    
                    <div class="step">
                        <div class="step-number">1</div>
                        <div>
                            <h3>Open Telegram</h3>
                            <p>Search for <strong>@terabox_download_genny_bot</strong></p>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">2</div>
                        <div>
                            <h3>Send Command</h3>
                            <div class="command-box">
                                /genny [terabox_link]
                            </div>
                            <p>Example: <code>/genny https://terabox.com/s/abc123</code></p>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">3</div>
                        <div>
                            <h3>Choose Method</h3>
                            <p>Select either:</p>
                            <p>• <strong>Direct Download</strong> - Get download link</p>
                            <p>• <strong>Telegram Download</strong> - Video sent in chat</p>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">4</div>
                        <div>
                            <h3>Download & Enjoy!</h3>
                            <p>Your video will be ready instantly</p>
                        </div>
                    </div>
                </div>
                
                <div class="bot-stats">
                    <h3 style="margin-bottom: 15px;">📊 API Status</h3>
                    <div id="apiStatus">
                        <div class="stat-item">
                            <span>Primary API:</span>
                            <span id="api1">Checking...</span>
                        </div>
                        <div class="stat-item">
                            <span>Bot API:</span>
                            <span id="api2">Checking...</span>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Made with <span class="heart">❤️</span> by <strong>Genny</strong></p>
                    <p>Channel: @NetFusionTG | GitHub: Account-Nahi he</p>
                    <p class="update-time" id="lastUpdate">Last updated: Just now</p>
                </div>
            </div>
        </div>
        
        <script>
            let startTime = Date.now();
            
            function updateUptime() {
                const now = Date.now();
                const diff = now - startTime;
                
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                
                document.getElementById('uptime').textContent = 
                    `${hours}h ${minutes}m ${seconds}s`;
            }
            
            function updateTime() {
                const now = new Date();
                const timeString = now.toLocaleTimeString();
                document.getElementById('lastUpdate').textContent = 
                    `Last updated: ${timeString}`;
            }
            
            async function checkAPIs() {
                try {
                    // Check bot status
                    const botResponse = await fetch('/health');
                    if (botResponse.ok) {
                        document.getElementById('api2').innerHTML = 
                            '<span style="color:#4CAF50">✅ Online</span>';
                    } else {
                        document.getElementById('api2').innerHTML = 
                            '<span style="color:#ff9800">⚠️ Warning</span>';
                    }
                    
                    // Check primary API
                    const apiResponse = await fetch('/api/status');
                    if (apiResponse.ok) {
                        const data = await apiResponse.json();
                        document.getElementById('api1').innerHTML = 
                            '<span style="color:#4CAF50">✅ Online</span>';
                        document.getElementById('sessionCount').textContent = data.sessions || 0;
                    }
                } catch (error) {
                    document.getElementById('api1').innerHTML = 
                        '<span style="color:#f44336">❌ Offline</span>';
                    document.getElementById('api2').innerHTML = 
                        '<span style="color:#f44336">❌ Offline</span>';
                }
            }
            
            // Initial updates
            updateUptime();
            updateTime();
            checkAPIs();
            
            // Update every 30 seconds
            setInterval(updateUptime, 1000);
            setInterval(updateTime, 30000);
            setInterval(checkAPIs, 30000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/health')
def health_check():
    return json.dumps({
        "status": "healthy",
        "service": "terabox-downloader-bot",
        "timestamp": time.time(),
        "version": "2.0.0"
    }), 200, {'Content-Type': 'application/json'}

@app.route('/api/status')
def api_status():
    return json.dumps({
        "bot": "online",
        "sessions": len(user_sessions),
        "active_users": list(user_sessions.keys()),
        "timestamp": time.time(),
        "server_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }), 200, {'Content-Type': 'application/json'}

# =============================
# TELEGRAM BOT FUNCTIONS
# =============================
def get_download_link(user_link):
    """Get download link from API"""
    try:
        api_url = f"{API_BASE}?key=RushVx&link={user_link}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.terabox.com/'
        }
        
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            
            # Try JSON
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                        item = data["data"][0]
                        if "download" in item:
                            return item["download"], item.get("title", "Video"), item.get("size", "Unknown")
                    elif "download_url" in data:
                        return data["download_url"], data.get("title", "Video"), data.get("size", "Unknown")
            except:
                pass
            
            # Search for URL
            patterns = [
                r'https://[a-zA-Z0-9._/-]+\.mp4(?:\?[^\s"]*)?',
                r'https://d\d+\.terabox\.com/[^\s"]+',
                r'https://[a-zA-Z0-9._/-]+nephobox\.com/[^\s"]+'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    url = match.group(0)
                    if len(url) > 20:
                        return url, "Video", "Unknown"
                        
    except Exception as e:
        print(f"API Error: {e}")
    
    return None, "Video", "Unknown"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = f"""
🎯 *Welcome to Terabox Downloader Bot* 🎯

*Available Commands:*
• /start - Show this message
• /genny [link] - Download Terabox video
• /help - Show help guide
• /credit - Show bot credits

✨ *Features:*
• Direct Download Links
• Telegram Direct Download
• Fast Processing
• Free Forever

{CREDIT_TEXT}

📌 *How to use:* Send /genny with Terabox link!
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def genny_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📝 *Usage:* `/genny [terabox_link]`\n\n"
            "Example: `/genny https://terabox.com/s/abc123`\n\n"
            "Please provide a Terabox link.",
            parse_mode='Markdown'
        )
        return
    
    user_link = ' '.join(context.args)
    user_id = update.effective_user.id
    chat_id = update.message.chat_id
    
    # Validate link
    if not user_link.startswith(('http://', 'https://')):
        await update.message.reply_text(
            "❌ *Invalid Link*\n\n"
            "Please send a valid URL starting with http:// or https://",
            parse_mode='Markdown'
        )
        return
    
    # Store session
    user_sessions[user_id] = {
        "link": user_link,
        "chat_id": chat_id,
        "timestamp": time.time()
    }
    
    # Show processing
    processing_msg = await update.message.reply_text(
        f"🔍 *Processing Your Request...*\n\n"
        f"📎 Link: `{user_link[:50]}...`\n\n"
        f"⏳ Fetching download information...\n\n"
        f"{CREDIT_TEXT}",
        parse_mode='Markdown'
    )
    
    # Get download link
    download_url, title, size = get_download_link(user_link)
    
    if download_url:
        user_sessions[user_id].update({
            "download_url": download_url,
            "title": title,
            "size": size
        })
        
        # Show options
        keyboard = [
            [
                InlineKeyboardButton("📥 DIRECT LINK", callback_data=f"direct_{user_id}"),
                InlineKeyboardButton("📲 TELEGRAM FILE", callback_data=f"telegram_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_msg.edit_text(
            f"✅ *Download Ready!*\n\n"
            f"📁 *Title:* `{title}`\n"
            f"📊 *Size:* `{size}`\n\n"
            f"*Choose download method:*\n\n"
            f"1. 📥 *DIRECT LINK* - Get download link\n"
            f"2. 📲 *TELEGRAM FILE* - Video sent in chat\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Auto-delete original after 2 seconds
        await asyncio.sleep(2)
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        except:
            pass
    else:
        await processing_msg.edit_text(
            f"❌ *Could Not Get Download Link*\n\n"
            f"Unable to fetch download for this link.\n\n"
            f"*Please check:*\n"
            f"• Link is valid and public\n"
            f"• Video is not removed\n"
            f"• Try again later\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown'
        )
        del user_sessions[user_id]

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
    if user_id not in user_sessions:
        await query.message.edit_text("⚠️ *Session expired*\n\nUse /genny command again.", parse_mode='Markdown')
        return
    
    user_data = user_sessions[user_id]
    download_url = user_data.get("download_url")
    title = user_data.get("title", "Video")
    size = user_data.get("size", "Unknown")
    
    if not download_url:
        await query.message.edit_text("❌ *No download link*\n\nTry again.", parse_mode='Markdown')
        return
    
    # Create download button
    keyboard = [[InlineKeyboardButton("📥 DOWNLOAD NOW", url=download_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        f"🔗 *Direct Download Link*\n\n"
        f"📁 *Title:* `{title}`\n"
        f"📊 *Size:* `{size}`\n\n"
        f"Click button to download:\n\n"
        f"{CREDIT_TEXT}",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    
    # Clean session
    if user_id in user_sessions:
        del user_sessions[user_id]

async def handle_telegram_download(query, context, user_id):
    if user_id not in user_sessions:
        await query.message.edit_text("⚠️ *Session expired*\n\nUse /genny command again.", parse_mode='Markdown')
        return
    
    user_data = user_sessions[user_id]
    download_url = user_data.get("download_url")
    title = user_data.get("title", "Video")
    chat_id = user_data["chat_id"]
    
    if not download_url:
        await query.message.edit_text("❌ *No download link*\n\nTry Direct Download.", parse_mode='Markdown')
        return
    
    await query.message.edit_text(
        f"⏬ *Downloading Video...*\n\n"
        f"📁 *Title:* `{title}`\n\n"
        f"⏳ Please wait...\n\n"
        f"{CREDIT_TEXT}",
        parse_mode='Markdown'
    )
    
    temp_path = None
    try:
        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
            temp_path = f.name
        
        # Download
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(download_url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Send video
            with open(temp_path, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    caption=f"🎬 *{title}*\n\n✅ Via @terabox_download_genny_bot\n\n{CREDIT_TEXT}",
                    parse_mode='Markdown',
                    supports_streaming=True
                )
            
            await query.message.delete()
            await context.bot.send_message(
                chat_id=chat_id,
                text="✅ *Video Sent Successfully!*\n\nEnjoy your video! 🎉\n\n🔔 @NetFusionTG",
                parse_mode='Markdown'
            )
            
        else:
            await query.message.edit_text(
                f"❌ *Download Failed*\n\n"
                f"Status: {response.status_code}\n"
                f"Try Direct Download option.\n\n"
                f"{CREDIT_TEXT}",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        print(f"Error: {e}")
        await query.message.edit_text(
            f"❌ *Error Downloading*\n\n"
            f"Try Direct Download option.\n\n"
            f"{CREDIT_TEXT}",
            parse_mode='Markdown'
        )
        
    finally:
        # Clean up
        if temp_path:
            try:
                import os
                os.remove(temp_path)
            except:
                pass
        
        if user_id in user_sessions:
            del user_sessions[user_id]

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = f"""
📖 *HELP GUIDE*

*Commands:*
/start - Start bot
/genny [link] - Download video
/help - This message
/credit - Credits

*How to Use:*
1. Send `/genny [terabox_link]`
2. Choose download method:
   • 📥 DIRECT LINK - Get download link
   • 📲 TELEGRAM FILE - Video sent in chat

*Features:*
• Fast download generation
• Two download options
• Auto-delete original links
• Free forever

*Note:* Some videos may have download restrictions.

{CREDIT_TEXT}
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def credit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(CREDIT_TEXT, parse_mode='Markdown')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

async def cleanup_sessions():
    """Clean old sessions"""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        current_time = time.time()
        to_delete = []
        
        for user_id, session in user_sessions.items():
            if current_time - session.get('timestamp', 0) > 600:  # 10 minutes
                to_delete.append(user_id)
        
        for user_id in to_delete:
            del user_sessions[user_id]
        
        if to_delete:
            print(f"Cleaned {len(to_delete)} sessions")

# =============================
# MAIN FUNCTIONS
# =============================
def run_web_server():
    """Run Flask web server"""
    app.run(host='0.0.0.0', port=PORT, debug=False)

def run_telegram_bot():
    """Run Telegram bot"""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("genny", genny_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("credit", credit_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    # Start cleanup task
    asyncio.get_event_loop().create_task(cleanup_sessions())
    
    print("🤖 Telegram Bot Starting...")
    application.run_polling()

def main():
    """Run both services"""
    import threading
    
    # Start Telegram bot in thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Start web server in main thread
    print(f"🌐 Web Server starting on port {PORT}...")
    run_web_server()

# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    # Check if running on Render
    if os.environ.get('RENDER', '').lower() == 'true':
        print("🚀 Running on Render Platform")
        print(f"🔧 Port: {PORT}")
        print(f"🤖 Bot Token: {'Set' if BOT_TOKEN and len(BOT_TOKEN) > 20 else 'Check'}")
        main()
    else:
        print("🏠 Running locally")
        run_telegram_bot()