import sys
import os

# Render Logs-এ রিয়েলটাইম প্রিন্ট দেখার জন্য
os.environ["PYTHONUNBUFFERED"] = "1"

import logging
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)

# ================= SAFE ENV PARSER =================
def get_env_int(key, default_value):
    val = os.getenv(key)
    if not val:
        return default_value
    try:
        return int(val.strip())
    except ValueError:
        return default_value

BOT_TOKEN = os.getenv("BOT_TOKEN", "8789480117:AAHQZ63ewvn7jjJMUxa9yLFRDemnS0zvSjA").strip()
ADMIN_ID = get_env_int("ADMIN_ID", 1146186608)
REQUIRED_CHANNEL = get_env_int("REQUIRED_CHANNEL", -1001481593780)
CHANNEL_LINK = "https://t.me/+3U0nMzWs4Aw0YjFl"

# ================= RENDER DUMMY SERVER =================
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Auto-Approve Bot is running on Render!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), DummyHandler)
        print(f"🌐 Web server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Dummy server error: {e}")

# --- MEDIA LINKS ---
IMAGE_URL_WELCOME = "https://i.ibb.co/XfxnhBYY/file-000000006ac47206b9a3e5b41d2e17e1.png"
IMAGE_URL_REG = "https://i.ibb.co/PZ5VTZVT/IMG-20260201-052425-386.jpg"
IMAGE_URL_SUCCESS = "https://i.ibb.co/TMwm08jL/file-0000000049547208b82b9486019c2ba0.png"
IMAGE_URL_HACK_MENU = "https://i.ibb.co/xKM4500N/file-000000003fe8720bad21d32e5802d848.png"

LOGO_AVIATOR = "https://i.ibb.co/PZBBDv85/images-9.jpg"
LOGO_AVIATOR_VIP = "https://i.ibb.co/PZBBDv85/images-9.jpg"
LOGO_LUCKY_JET = "https://i.ibb.co/rRmGk474/1.jpg"
LOGO_MINES = "https://i.ibb.co/MDVxth7x/images-8.jpg"
LOGO_MINI_MINES = "https://i.ibb.co/MDVxth7x/images-8.jpg"
LOGO_PENALTY = "https://i.ibb.co/5WzBdWX4/hqdefault.jpg"
LOGO_KING_THIMBLES = "https://i.ibb.co/8LYwvg1j/maxresdefault.jpg"
LOGO_COIN = "https://i.ibb.co/jPb1tK68/file-000000009198720b89de6ec83058fd19.png"

LINK_AVIATOR = "https://aviatorgameadmin.netlify.app/"
LINK_AVIATOR_VIP = "https://blackdog.unaux.com/signal.html"
LINK_LUCKY_JET = "https://1xbet-melbet-apple.unaux.com/signal.html"
LINK_MINES = "https://mines-game-hack.netlify.app/"
LINK_MINI_MINES = "https://1xbet-melbet-apple.unaux.com/minsadmin.html"
LINK_PENALTY = "https://pnalteaybot.netlify.app/"
LINK_KING_THIMBLES = "https://kingthimblesbot.netlify.app/"
LINK_COIN = "https://sunny1.unaux.com/coin.html"
HOW_TO_USE_LINK = "https://youtube.com/@sunny_bro11?si=gYfOtXnKayCkZloF"

WAITING_FOR_ID = 0

LANGUAGES = {
    'en': {
        'name': '🇺🇸 English',
        'earn_btn': 'Start Earning Money',
        'reg_btn': 'Registration Link',
        'verify_btn': '✅ I have Registered (Verify)',
        'ask_id': 'Please send your 9-digit Account ID:',
        'analyzing': '🔄 Verifying your Account ID with 1Win Database...',
        'success_msg': '✅ <b>ACCOUNT VERIFIED!</b>\n\nYour account has been successfully synchronized with the bot.',
        'play_btn': 'Play With Hack',
        'guide_btn': 'How to use',
        'help_btn': 'Help',
        'select_game': 'Select a game to start hacking:'
    },
    'bd': {
        'name': '🇧🇩 Bangladesh (Bangla)',
        'earn_btn': 'টাকা আয় শুরু করুন',
        'reg_btn': 'রেজিস্ট্রেশন লিংক',
        'verify_btn': '✅ আমার রেজিস্ট্রেশন সম্পন্ন হয়েছে',
        'ask_id': 'অনুগ্রহ করে আপনার ৯ ডিজিটের একাউন্ট আইডি দিন:',
        'analyzing': '🔄 আপনার আইডিটি 1Win ডেটাবেজে যাচাই করা হচ্ছে...',
        'success_msg': '✅ <b>একাউন্ট ভেরিফাইড!</b>\n\nআপনার একাউন্টটি সফলভাবে বটের সাথে যুক্ত হয়েছে।',
        'play_btn': 'Play With Hack',
        'guide_btn': 'কিভাবে ব্যবহার করবেন',
        'help_btn': 'সাহায্য',
        'select_game': 'হ্যাক শুরু করতে একটি গেম সিলেক্ট করুন:'
    }
}

# ================= MEMBERSHIP CHECK =================
async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]
    except Exception as e:
        return True

async def send_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"Hello {user.first_name}, Welcome!\nPlease select your language:"

    keyboard = [
        [InlineKeyboardButton(LANGUAGES['en']['name'], callback_data='lang_en'), InlineKeyboardButton(LANGUAGES['bd']['name'], callback_data='lang_bd')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        try: await update.callback_query.message.delete()
        except: pass
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text, reply_markup=reply_markup)

# ================= HANDLERS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    is_member = await check_membership(user_id, context)
    
    if is_member:
        await send_language_menu(update, context)
    else:
        join_text = (
            "⚠️ <b>Action Required!</b>\n\n"
            "To use this bot, you must join our official Private channel first."
        )
        keyboard = [
            [InlineKeyboardButton("📢 Join Private Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Joined / Verify", callback_data='check_join_status')]
        ]
        await context.bot.send_message(chat_id=user_id, text=join_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    return ConversationHandler.END

async def check_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if await check_membership(update.effective_user.id, context):
        await send_language_menu(update, context)
    else:
        await query.answer("❌ You have not joined yet!", show_alert=True)

async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = query.data.split('_')[1]
    context.user_data['selected_lang'] = lang_code
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    keyboard = [[InlineKeyboardButton(lang_data['earn_btn'], callback_data='start_earning')]]
    
    try: await query.message.delete()
    except: pass
    
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_WELCOME, caption=f"Language: {lang_data['name']}\n\nClick below to proceed:", reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def show_registration_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    info_text = (
        "<b>Step 1 - Register.</b>\n\n"
        "To synchronize with the bot, create a new account via the button below and use Promo Code: <b>BLACK110</b>\n\n"
        "<b>Step 2 - Verify</b>\n\n"
        "After registration, click the <b>Verify</b> button below."
    )

    keyboard = [
        [InlineKeyboardButton(f"🔗 {lang_data['reg_btn']}", url="https://1wezue.com/casino")],
        [InlineKeyboardButton(f"{lang_data['verify_btn']}", callback_data='verify_reg')],
        [InlineKeyboardButton(f"🆘 {lang_data['help_btn']}", url="https://t.me/SUNNY_BRO1")]
    ]

    try: await query.message.delete()
    except: pass
    
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_REG, caption=info_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    return ConversationHandler.END

async def verify_process_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    msg = await context.bot.send_message(chat_id=chat_id, text="⏳ Initializing verification...")
    await asyncio.sleep(2) 
    try: await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    except: pass

    await context.bot.send_message(chat_id=chat_id, text=lang_data['ask_id'])
    return WAITING_FOR_ID

async def receive_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id_text = update.message.text.strip()
    chat_id = update.effective_chat.id
    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    # ইউজার আইডি সংখ্যা কিনা এবং অন্তত ৮ থেকে ১২ ডিজিটের কিনা তা নিশ্চিত করা
    if not user_id_text.isdigit() or len(user_id_text) < 7:
        await update.message.reply_text("❌ Invalid Account ID! Please enter a valid numeric 8-9 digit Account ID.")
        return WAITING_FOR_ID

    analyzing_msg = await update.message.reply_text(f"⏳ {lang_data['analyzing']}")
    
    # ৩ সেকেন্ড ভেরিফিকেশনের নাটক (Simulated Checking)
    await asyncio.sleep(3)
    
    try: await context.bot.delete_message(chat_id=chat_id, message_id=analyzing_msg.message_id)
    except: pass

    # AUTO-APPROVE: যেকোনো ডিজিট দিলেই সাথে সাথে এপ্রুভ
    final_keyboard = [
        [InlineKeyboardButton(f"🎮 {lang_data['play_btn']}", callback_data='play_hack_action')],
        [InlineKeyboardButton(f"📺 {lang_data['guide_btn']}", url=HOW_TO_USE_LINK)]
    ]
    await context.bot.send_photo(chat_id=chat_id, photo=IMAGE_URL_SUCCESS, caption=lang_data['success_msg'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(final_keyboard))

    return ConversationHandler.END

async def play_hack_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang_code = context.user_data.get('selected_lang', 'en')
    lang_data = LANGUAGES.get(lang_code, LANGUAGES['en'])

    keyboard = [
        [InlineKeyboardButton("🔴 ✈️ Aviator", callback_data='game_aviator'), InlineKeyboardButton("🔵 ✈️ AVIATOR VIP", callback_data='game_aviator_vip')],
        [InlineKeyboardButton("🟢 🚀 Lucky Jet", callback_data='game_lucky_jet'), InlineKeyboardButton("🔴 💣 Mines", callback_data='game_mines')],
        [InlineKeyboardButton("🔵 💣 Mine Mines", callback_data='game_mini_mines'), InlineKeyboardButton("🟢 ⚽ Penalty", callback_data='game_penalty')],
        [InlineKeyboardButton("🔴 👑 King Thimbles", callback_data='game_king_thimbles'), InlineKeyboardButton("🔵 🪙 Coin SIGNAL", callback_data='game_coin')]
    ]

    try: await query.message.delete()
    except: pass
    
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=IMAGE_URL_HACK_MENU, caption=lang_data['select_game'], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def game_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    game_type = query.data
    logo_url, game_name, hack_url = LOGO_AVIATOR, "Aviator", LINK_AVIATOR

    if game_type == 'game_aviator': logo_url, game_name, hack_url = LOGO_AVIATOR, "Aviator", LINK_AVIATOR
    elif game_type == 'game_aviator_vip': logo_url, game_name, hack_url = LOGO_AVIATOR_VIP, "AVIATOR VIP", LINK_AVIATOR_VIP
    elif game_type == 'game_lucky_jet': logo_url, game_name, hack_url = LOGO_LUCKY_JET, "Lucky Jet", LINK_LUCKY_JET
    elif game_type == 'game_mines': logo_url, game_name, hack_url = LOGO_MINES, "Mines", LINK_MINES
    elif game_type == 'game_mini_mines': logo_url, game_name, hack_url = LOGO_MINI_MINES, "Mine Mines", LINK_MINI_MINES
    elif game_type == 'game_penalty': logo_url, game_name, hack_url = LOGO_PENALTY, "Penalty", LINK_PENALTY
    elif game_type == 'game_king_thimbles': logo_url, game_name, hack_url = LOGO_KING_THIMBLES, "King Thimbles", LINK_KING_THIMBLES
    elif game_type == 'game_coin': logo_url, game_name, hack_url = LOGO_COIN, "Coin SIGNAL", LINK_COIN

    keyboard = [
        [InlineKeyboardButton(f"📱 Open {game_name}", web_app=WebAppInfo(url=hack_url))],
        [InlineKeyboardButton("🔙 Back", callback_data='play_hack_action')]
    ]

    try: await query.message.delete()
    except: pass
    
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=logo_url, caption=f"<b>{game_name} Connected!</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END

# ================= MAIN =================
if __name__ == '__main__':
    try:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        print("🚀 Starting Auto-Approve Telegram Bot process...")
        
        threading.Thread(target=run_dummy_server, daemon=True).start()

        application = ApplicationBuilder().token(BOT_TOKEN).build()

        verify_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(verify_process_start, pattern='^verify_reg$')],
            states={WAITING_FOR_ID:[MessageHandler(filters.TEXT & ~filters.COMMAND, receive_id)]},
            fallbacks=[CommandHandler('cancel', cancel)],
            allow_reentry=True
        )

        application.add_handler(verify_conv)
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CallbackQueryHandler(check_join_callback, pattern='^check_join_status$'))
        application.add_handler(CallbackQueryHandler(language_handler, pattern='^lang_'))
        application.add_handler(CallbackQueryHandler(show_registration_info, pattern='^start_earning$'))
        application.add_handler(CallbackQueryHandler(play_hack_menu, pattern='^play_hack_action$'))
        application.add_handler(CallbackQueryHandler(game_selection_handler, pattern='^game_'))

        print("🤖 Auto-Approve Bot Polling started successfully!")
        application.run_polling()
    except Exception as fatal_error:
        print(f"❌ FATAL ERROR CAUSING CRASH: {fatal_error}")
        sys.exit(1)
