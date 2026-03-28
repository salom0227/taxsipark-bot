"""
🚖 TaxsiPark Bot — Webhook versiyasi (Render uchun eng barqaror)
"""

import logging
import os
from fastapi import FastAPI, Request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

# ══════════════════════════════════════════
BOT_TOKEN = "8794761249:AAG7s6z51Y0yDoZjJJ6SwxoicTd30u3vIIA"
ADMIN_1_USERNAME = "ibrokhim_515"
ADMIN_2_USERNAME = "SAFARGO_TAXI"
RENDER_URL = "https://taxsipark-bot.onrender.com"
WELCOME_IMAGE = "welcome.png"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"
# ══════════════════════════════════════════

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

WAIT_START, ASK_NAME, ASK_PHONE, MAIN_MENU, TAXSIPARK_MENU = range(5)

# ══════════════════════════════════════════
#   KLAVIATURALAR
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
#   HANDLERS
# ══════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    caption = "👋 Salom! 🚖 <b>TaxsiPark</b> botiga xush kelibsiz!\n\nDavom etish uchun <b>🚀 START</b> tugmasini bosing 👇"
    try:
        if os.path.exists(WELCOME_IMAGE):
            with open(WELCOME_IMAGE, "rb") as photo:
                await update.message.reply_photo(photo=photo, caption=caption, parse_mode="HTML", reply_markup=kb_start())
        else:
            await update.message.reply_text(caption, parse_mode="HTML", reply_markup=kb_start())
    except Exception as e:
        logger.error(f"Rasm xatosi: {e}")
        await update.message.reply_text(caption, parse_mode="HTML", reply_markup=kb_start())
    return WAIT_START

async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✏️ <b>To'liq ismingizni</b> kiriting (F.I.Sh):", parse_mode="HTML")
    return ASK_NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📱 Telefon raqamingizni yuboring:", reply_markup=kb_phone())
    return ASK_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number if update.message.contact else update.message.text
    context.user_data["phone"] = phone
    await update.message.reply_text(
        f"✅ Ro'yxatdan o'tdingiz!\n\n👤 <b>{context.user_data['name']}</b>\n📱 <b>{phone}</b>",
        parse_mode="HTML", reply_markup=kb_main()
    )
    return MAIN_MENU

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🚖 TaxsiPark haqida":
        await update.message.reply_text("🚖 Bo'limni tanlang:", reply_markup=kb_taxsipark())
        return TAXSIPARK_MENU
    elif text == "📞 Bog'lanish":
        await update.message.reply_text(
            f"📞 Adminlar:\n\n👤 @{ADMIN_1_USERNAME}\n👤 @{ADMIN_2_USERNAME}",
            reply_markup=kb_main()
        )
    return MAIN_MENU

async def handle_taxsipark_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📄 Hujjat yuborish":
        await update.message.reply_text("⬇️ Adminni tanlang:", reply_markup=kb_admins())
    elif text == "ℹ️ Ma'lumot":
        await update.message.reply_text("🚖 TaxsiPark — haydovchilar uchun tezkor ro'yxatdan o'tish tizimi🚖 Safargo — haydovchilar uchun eng qulay taksopark! 🚖

Assalomu alaykum! 👋
Safargo sizga nafaqat ish, balki barqaror daromad va bonuslar ham beradi 💸

🎁 Start bonus:
Ro‘yxatdan o‘tganingiz zahoti 40 000 so‘m bonus sizniki!

🔥 Har oy sovg‘alar:
Safargo’da har oy yangi bonus va aksiyalar bo‘lib turadi 🎉

👨‍👨‍👦 Do‘st olib keling – pul ishlang:
Har bir do‘st uchun 50 000 so‘m
(50 ta zakaz bajargach beriladi) 💰

📉 Minimal foiz:
Atigi 2,2% — siz uchun maksimal foyda ⚡

🏆 Katta balans = katta bonus:
1 mln so‘m yig‘ing — 50 000 so‘m bonus oling 🎯

💳 Qulay to‘lov:
Click / Payme orqali to‘ldiring va 5% keshbek oling 🔥

📜 Ishonch va rasmiylik:
Safargo — sertifikatlangan taksopark ✔️

🚘 Qo‘shimcha imkoniyatlar:
✅ Litsenziya nakleyka
✅ Komfort / Komfort+ ochish
✅ Blokdan chiqarish xizmati

🚀 Safargo bilan ishlash — bu o‘sish, daromad va qulaylik!
Bugunoq bizga qo‘shiling🔥  .")
    elif text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=kb_main())
        return MAIN_MENU
    return TAXSIPARK_MENU

# ══════════════════════════════════════════
#   FASTAPI + WEBHOOK
# ══════════════════════════════════════════

# PTB Application — global
ptb_app = Application.builder().token(BOT_TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", cmd_start)],
    states={
        WAIT_START:     [MessageHandler(filters.Regex("^🚀 START$"), handle_start_button)],
        ASK_NAME:       [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
        ASK_PHONE:      [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), handle_phone)],
        MAIN_MENU:      [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        TAXSIPARK_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_taxsipark_menu)],
    },
    fallbacks=[CommandHandler("start", cmd_start)],
)
ptb_app.add_handler(conv)

# FastAPI
web = FastAPI()

@web.get("/")
@web.get("/health")
async def health():
    return {"status": "ok"}

@web.post(WEBHOOK_PATH)
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.process_update(update)
    return {"ok": True}

@web.on_event("startup")
async def startup():
    await ptb_app.initialize()
    await ptb_app.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"✅ Webhook o'rnatildi: {WEBHOOK_URL}")

@web.on_event("shutdown")
async def shutdown():
    await ptb_app.shutdown()
```

## `requirements.txt`
```
python-telegram-bot[job-queue]==21.3
fastapi
uvicorn
httpx
