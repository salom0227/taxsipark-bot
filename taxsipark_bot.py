"""
🚖 TaxsiPark Telegram Bot - Full Version for Render
"""

import logging
import os
import asyncio
import threading
import http.server
import socketserver
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ══════════════════════════════════════════
#            SOZLAMALAR
# ══════════════════════════════════════════

BOT_TOKEN = "8794761249:AAFZmEk3uOiOftuGFW15fhuvz170ITWiI4I"
ADMIN_1_USERNAME = "ibrokhim_515"
ADMIN_2_USERNAME = "SAFARGO_TAXI"
WELCOME_IMAGE = "welcome.png"

# ══════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

(
    WAIT_START,
    ASK_NAME,
    ASK_PHONE,
    MAIN_MENU,
    TAXSIPARK_MENU,
) = range(5)

# ══════════════════════════════════════════
#      RENDER UCHUN SOXTA SERVER (PORT)
# ══════════════════════════════════════════

def run_fake_server():
    """Render o'chirib qo'ymasligi uchun soxta port ochish"""
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            logger.info(f"Render uchun soxta server {port}-portda ishga tushdi")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"Server xatosi: {e}")

# ══════════════════════════════════════════
#            KLAVIATURALAR
# ══════════════════════════════════════════

def kb_start():
    return ReplyKeyboardMarkup([[KeyboardButton("🚀 START")]], resize_keyboard=True, one_time_keyboard=True)

def kb_phone():
    return ReplyKeyboardMarkup([[KeyboardButton("📱 Raqamni avtomatik yuborish", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)

def kb_main():
    return ReplyKeyboardMarkup([["🚖 TaxsiPark haqida"], ["📞 Bog'lanish"]], resize_keyboard=True)

def kb_taxsipark():
    return ReplyKeyboardMarkup([["📄 Hujjat yuborish"], ["ℹ️ Ma'lumot"], ["🔙 Orqaga"]], resize_keyboard=True)

def kb_admins():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Admin 1", url=f"https://t.me/{ADMIN_1_USERNAME}")],
        [InlineKeyboardButton("👤 Admin 2", url=f"https://t.me/{ADMIN_2_USERNAME}")]
    ])

# ══════════════════════════════════════════
#            HANDLERS
# ══════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    caption = "👋 Salom! 🚖 <b>TaxsiPark</b> botiga xush kelibsiz!\n\nDavom etish uchun <b>START</b> tugmasini bosing 👇"
    
    try:
        if os.path.exists(WELCOME_IMAGE):
            with open(WELCOME_IMAGE, "rb") as photo:
                await update.message.reply_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=kb_start())
        else:
            await update.message.reply_text(caption, parse_mode="HTML", reply_markup=kb_start())
    except:
        await update.message.reply_text(caption, parse_mode="HTML", reply_markup=kb_start())
    return WAIT_START

async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ Iltimos, <b>to'liq ismingizni</b> kiriting:", parse_mode="HTML")
    return ASK_NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📱 Endi telefon raqamingizni yuboring:", reply_markup=kb_phone())
    return ASK_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text
    context.user_data["phone"] = phone
    
    await update.message.reply_text(f"✅ Ro'yxatdan o'tdingiz!\n👤 Ism: {context.user_data['name']}\n📱 Tel: {phone}", reply_markup=kb_main())
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🚖 TaxsiPark haqida":
        await update.message.reply_text("🚖 Bo'limni tanlang:", reply_markup=kb_taxsipark())
        return TAXSIPARK_MENU
    elif text == "📞 Bog'lanish":
        await update.message.reply_text(f"📞 Adminlar:\n@{ADMIN_1_USERNAME}\n@{ADMIN_2_USERNAME}", reply_markup=kb_main())
    return MAIN_MENU

async def handle_taxsipark_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📄 Hujjat yuborish":
        await update.message.reply_text("⬇️ Hujjatlarni yuborish uchun adminni tanlang:", reply_markup=kb_admins())
    elif text == "ℹ️ Ma'lumot":
        await update.message.reply_text("🚖 TaxsiPark - haydovchilar uchun qulay tizim.")
    elif text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=kb_main())
        return MAIN_MENU
    return TAXSIPARK_MENU

# ══════════════════════════════════════════
#            MAIN
# ══════════════════════════════════════════

def main():
    # Render o'chirib qo'ymasligi uchun portni alohida thread'da ochamiz
    threading.Thread(target=run_fake_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            WAIT_START: [MessageHandler(filters.Regex("^🚀 START$"), handle_start_button)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            ASK_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), handle_phone)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
            TAXSIPARK_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_taxsipark_menu)],
        },
        fallbacks=[CommandHandler("start", cmd_start)],
    )

    app.add_handler(conv)
    logger.info("Bot pollingni boshladi...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
