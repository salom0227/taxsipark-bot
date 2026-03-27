"""
🚖 TaxsiPark Telegram Bot - Final Stable Version for Render (No Sleep)
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
# Botni uyg'otib turish uchun kerak:
import httpx 

# ══════════════════════════════════════════
#            SOZLAMALAR
# ══════════════════════════════════════════

# Botingizning Telegram Tokeni
BOT_TOKEN = "8794761249:AAG7s6z51Y0yDoZjJJ6SwxoicTd30u3vIIA"

# Adminlarning Telegram username'lari (boshida @ belgisiz)
ADMIN_1_USERNAME = "ibrokhim_515"
ADMIN_2_USERNAME = "SAFARGO_TAXI"

# Botingizning Render'dagi to'liq URL manzili (Self-ping uchun juda muhim!)
# O'zingizning Render Dashboard'ingizdan ko'rib to'g'rilang!
RENDER_URL = "https://taxsipark-bot.onrender.com" 

# Salomlashish rasmi fayl nomi (GitHub'da bo'lishi kerak)
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
#      1. RENDER UCHUN SOXTA SERVER (PORT)
# ══════════════════════════════════════════

def run_fake_server():
    """Render o'chirib qo'ymasligi uchun soxta port ochish"""
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        # Portni ochish va so'rovlarni qabul qilish
        with socketserver.TCPServer(("", port), handler) as httpd:
            logger.info(f"  🛰  Render uchun soxta server {port}-portda ishga tushdi")
            httpd.serve_forever()
    except Exception as e:
        logger.error(f"❌ Soxta server xatosi: {e}")

# ══════════════════════════════════════════
#      2. KEEP ALIVE (SELF-PING - HAR 4 DAQIQA)
# ══════════════════════════════════════════

async def keep_alive():
    """Botni Renderda uyg'oq ushlab turish uchun o'ziga o'zi so'rov yuborish"""
    logger.info("  ⏰ Self-ping (Keep Alive) funksiyasi ishga tushdi...")
    
    # httpx klienti yordamida so'rov yuborish
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # O'zimizning Render URL'ga GET so'rovi yuboramiz
                response = await client.get(RENDER_URL)
                if response.status_code == 200:
                    logger.info(f"  ⏰ Self-ping muvaffaqiyatli: {response.status_code} OK")
                else:
                    logger.warning(f"  ⏰ Self-ping kutilmagan status: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Self-ping xatosi: {e}")
            
            # Har 4 daqiqada (240 soniya) so'rov yuboradi
            await asyncio.sleep(240)

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
    """Botga START buyrug'i kelganda chaqiriladi"""
    # Foydalanuvchi ma'lumotlarini tozalash
    context.user_data.clear()
    
    caption = "👋 Salom! 🚖 <b>TaxsiPark</b> botiga xush kelibsiz!\n\nRo'yxatdan o'tish va davom etish uchun <b>🚀 START</b> tugmasini bosing 👇"
    
    try:
        # Agar rasm fayli mavjud bo'lsa, uni yuboramiz
        if os.path.exists(WELCOME_IMAGE):
            with open(WELCOME_IMAGE, "rb") as photo:
                await update.message.reply_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=kb_start())
        else:
            # Agar rasm bo'lmasa, faqat matn
            await update.message.reply_text(caption, parse_mode="HTML", reply_markup=kb_start())
    except Exception as e:
        logger.error(f"Rasm yuborishda xato: {e}")
        await update.message.reply_text(caption, parse_mode="HTML", reply_markup=kb_start())
        
    return WAIT_START

async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi 'START' tugmasini bosganda"""
    await update.message.reply_text("✏️ Iltimos, <b>to'liq ismingizni</b> (Familiya Ism Sharif) kiriting:", parse_mode="HTML")
    return ASK_NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi ismini kiritganda"""
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📱 Endi telefon raqamingizni pastdagi tugma orqali yuboring:", reply_markup=kb_phone())
    return ASK_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi telefon raqamini yuborganda"""
    # Kontakt orqali yoki matn sifatida yuborilganini tekshiramiz
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text
        
    context.user_data["phone"] = phone
    
    # Ro'yxatdan o'tish muvaffaqiyatli tugaganini bildiramiz
    await update.message.reply_text(
        f"✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n\n"
        f"👤 Ism: <b>{context.user_data['name']}</b>\n"
        f"📱 Tel: <b>{phone}</b>", 
        parse_mode="HTML",
        reply_markup=kb_main()
    )
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy menyu tugmalari bosilganda"""
    text = update.message.text
    
    if text == "🚖 TaxsiPark haqida":
        await update.message.reply_text("🚖 Kerakli bo'limni tanlang:", reply_markup=kb_taxsipark())
        return TAXSIPARK_MENU
    elif text == "📞 Bog'lanish":
        # Adminlar bilan bog'lanish ma'lumotlarini yuboramiz
        await update.message.reply_text(
            f"📞 Adminlar bilan bog'lanish:\n\n"
            f"👤 Admin 1: @{ADMIN_1_USERNAME}\n"
            f"👤 Admin 2: @{ADMIN_2_USERNAME}", 
            reply_markup=kb_main()
        )
        
    return MAIN_MENU

async def handle_taxsipark_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TaxsiPark menyusi tugmalari bosilganda"""
    text = update.message.text
    
    if text == "📄 Hujjat yuborish":
        # Hujjat yuborish uchun admin profillariga link beramiz
        await update.message.reply_text(
            "⬇️ Hujjatlarni (haydovchilik guvohnomasi, pasport va h.k.) yuborish uchun pastdagi adminlardan birini tanlang:", 
            reply_markup=kb_admins()
        )
    elif text == "ℹ️ Ma'lumot":
        await update.message.reply_text("🚖 TaxsiPark - haydovchilar uchun qulay va tezkor ro'yxatdan o'tish tizimi.")
    elif text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=kb_main())
        return MAIN_MENU
        
    return TAXSIPARK_MENU

# ══════════════════════════════════════════
#            MAIN
# ══════════════════════════════════════════

def main():
    """Botni ishga tushirish funksiyasi"""
    
    # 1. Render o'chirib qo'ymasligi uchun portni alohida tishda (thread) ochamiz
    threading.Thread(target=run_fake_server, daemon=True).start()
    
    # 2. Bot ilovasini yaratamiz
    app = Application.builder().token(BOT_TOKEN).build()
    
    # 3. Self-ping (Keep Alive) funksiyasini asyncio loopda ishga tushirish
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # create_task loop ishga tushgandan keyin bajariladi
    app.job_queue.run_once(lambda context: loop.create_task(keep_alive()), 5)

    # 4. Ro'yxatdan o'tish va menyu handlerlarini qo'shamiz (ConversationHandler)
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
    
    # 5. Bot pollingni boshlaydi (Telegramdan xabarlarni so'rab oladi)
    logger.info("🚀 Bot pollingni boshladi (Tayyor)...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
