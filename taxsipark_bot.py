"""
🚖 Taksopark Bot — Webhook versiyasi (Render uchun eng barqaror)
"""

import logging
import os
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
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
#   SOZLAMALAR
# ══════════════════════════════════════════

BOT_TOKEN      = "8670099128:AAEaLw1r4GmoVHPOjgk8NXCKJQbksxY5-co"
ADMIN_USERNAME = "SAFARGO_TAXI"
RENDER_URL     = os.environ.get("RENDER_URL", "https://taxsipark-bot.onrender.com")
WELCOME_IMAGE  = "welcome.png"
WEBHOOK_PATH   = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL    = f"{RENDER_URL}{WEBHOOK_PATH}"

# ══════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

MAIN_MENU, MALUMOT_STATE, ROYHATTAN_NAME, ROYHATTAN_PHONE = range(4)

# ══════════════════════════════════════════
#   KLAVIATURALAR
# ══════════════════════════════════════════

def kb_main():
    return ReplyKeyboardMarkup(
        [
            ["🚖 Taksopark haqida ma'lumot olish"],
            ["📝 Ro'yxatdan o'tish"],
            ["📞 Operator bilan bog'lanish"],
            ["📄 Texpasport va pravangizni yuboring"],
        ],
        resize_keyboard=True
    )

def kb_phone():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni avtomatik yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def kb_back():
    return ReplyKeyboardMarkup(
        [["🔙 Orqaga"]],
        resize_keyboard=True
    )

def kb_admin_link():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Hujjatlarni yuborish", url=f"https://t.me/{ADMIN_USERNAME}")]
    ])

# ══════════════════════════════════════════
#   MALUMOT MATNI
# ══════════════════════════════════════════

MALUMOT_MATNI = (
    "🚖 Taksopark — haydovchilar uchun tezkor ro'yxatdan o'tish tizimi\n"
    "🚖 Safargo — haydovchilar uchun eng qulay taksopark!\n\n"
    "Assalomu alaykum! 👋\n"
    "Safargo sizga nafaqat ish, balki barqaror daromad va bonuslar ham beradi 💸\n\n"
    "🎁 Start bonus:\n"
    "Ro'yxatdan o'tganingiz zahoti 40 000 so'm bonus sizniki!\n\n"
    "🔥 Har oy sovg'alar:\n"
    "Safargo'da har oy yangi bonus va aksiyalar bo'lib turadi 🎉\n\n"
    "👨‍👨‍👦 Do'st olib keling – pul ishlang:\n"
    "Har bir do'st uchun 50 000 so'm\n"
    "(50 ta zakaz bajargach beriladi) 💰\n\n"
    "📉 Minimal foiz:\n"
    "Atigi 2,2% — siz uchun maksimal foyda ⚡\n\n"
    "🏆 Katta balans = katta bonus:\n"
    "1 mln so'm yig'ing — 50 000 so'm bonus oling 🎯\n\n"
    "💳 Qulay to'lov:\n"
    "Click / Payme orqali to'ldiring va 5% keshbek oling 🔥\n\n"
    "📜 Ishonch va rasmiylik:\n"
    "Safargo — sertifikatlangan taksopark ✔️\n\n"
    "🚘 Qo'shimcha imkoniyatlar:\n"
    "✅ Litsenziya nakleyka\n"
    "✅ Komfort / Komfort+ ochish\n"
    "✅ Blokdan chiqarish xizmati\n\n"
    "🚀 Safargo bilan ishlash — bu o'sish, daromad va qulaylik!\n"
    "Bugunoq bizga qo'shiling 🔥"
)

BOGLANISH_MATNI = (
    "📞 Operator bilan bog'lanish:\n\n"
    "📱 Telefon: +998(55)515-00-54\n"
)

# ══════════════════════════════════════════
#   HANDLERS
# ══════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    caption = (
        "👋 Salom! 🚖 <b>Taksopark</b> botiga xush kelibsiz!\n\n"
        "Quyidagi bo'limlardan birini tanlang 👇"
    )
    try:
        if os.path.exists(WELCOME_IMAGE):
            with open(WELCOME_IMAGE, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo, caption=caption,
                    parse_mode="HTML", reply_markup=kb_main()
                )
        else:
            await update.message.reply_text(
                caption, parse_mode="HTML", reply_markup=kb_main()
            )
    except Exception as e:
        logger.error(f"Rasm xatosi: {e}")
        await update.message.reply_text(
            caption, parse_mode="HTML", reply_markup=kb_main()
        )
    return MAIN_MENU


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🚖 Taksopark haqida ma'lumot olish":
        await update.message.reply_text(MALUMOT_MATNI, reply_markup=kb_main())
        return MAIN_MENU

    elif text == "📝 Ro'yxatdan o'tish":
        await update.message.reply_text(
            "✏️ <b>To'liq ismingizni</b> kiriting (F.I.Sh):",
            parse_mode="HTML",
            reply_markup=kb_back()
        )
        return ROYHATTAN_NAME

    elif text == "📞 Operator bilan bog'lanish":
        await update.message.reply_text(BOGLANISH_MATNI, reply_markup=kb_main())
        return MAIN_MENU

    elif text == "📄 Texpasport va pravangizni yuboring":
        await update.message.reply_text(
            "📄 Texpasport va pravangizni yuboring!\n\n"
            "Quyidagi tugmani bosib adminimizga hujjatlaringizni yuboring 👇",
            reply_markup=kb_admin_link()
        )
        return MAIN_MENU

    return MAIN_MENU


async def handle_royhattan_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=kb_main())
        return MAIN_MENU
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "📱 Telefon raqamingizni yuboring:",
        reply_markup=kb_phone()
    )
    return ROYHATTAN_PHONE


async def handle_royhattan_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text == "🔙 Orqaga":
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=kb_main())
        return MAIN_MENU
    phone = (
        update.message.contact.phone_number
        if update.message.contact
        else update.message.text
    )
    context.user_data["phone"] = phone
    await update.message.reply_text(
        f"✅ Ro'yxatdan o'tdingiz!\n\n"
        f"👤 <b>{context.user_data.get('name', '')}</b>\n"
        f"📱 <b>{phone}</b>\n\n"
        f"Tez orada operator siz bilan bog'lanadi! 🚖",
        parse_mode="HTML",
        reply_markup=kb_main()
    )
    return MAIN_MENU


async def global_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot restart bo'lsa ham tugmalar ishlaydi"""
    text = update.message.text

    if text == "🚖 Taksopark haqida ma'lumot olish":
        await update.message.reply_text(MALUMOT_MATNI, reply_markup=kb_main())
    elif text == "📝 Ro'yxatdan o'tish":
        await update.message.reply_text(
            "✏️ <b>To'liq ismingizni</b> kiriting (F.I.Sh):",
            parse_mode="HTML",
            reply_markup=kb_back()
        )
    elif text == "📞 Operator bilan bog'lanish":
        await update.message.reply_text(BOGLANISH_MATNI, reply_markup=kb_main())
    elif text == "📄 Texpasport va pravangizni yuboring":
        await update.message.reply_text(
            "📄 Texpasport va pravangizni yuboring!\n\n"
            "Quyidagi tugmani bosib adminimizga hujjatlaringizni yuboring 👇",
            reply_markup=kb_admin_link()
        )
    else:
        await update.message.reply_text(
            "Iltimos, /start buyrug'ini bosing.", reply_markup=kb_main()
        )

# ══════════════════════════════════════════
#   KEEP ALIVE
# ══════════════════════════════════════════

async def keep_alive():
    """Har 10 daqiqada o'ziga ping — Render uxlamasin"""
    while True:
        await asyncio.sleep(600)
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{RENDER_URL}/health", timeout=10)
                logger.info(f"⏰ Keep-alive: {r.status_code}")
        except Exception as e:
            logger.warning(f"⏰ Keep-alive xatosi: {e}")

# ══════════════════════════════════════════
#   PTB APPLICATION
# ══════════════════════════════════════════

ptb_app = Application.builder().token(BOT_TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", cmd_start)],
    states={
        MAIN_MENU:       [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)],
        ROYHATTAN_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_royhattan_name)],
        ROYHATTAN_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), handle_royhattan_phone)],
    },
    fallbacks=[CommandHandler("start", cmd_start)],
    allow_reentry=True,
)
ptb_app.add_handler(conv)
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, global_fallback))

# ══════════════════════════════════════════
#   FASTAPI
# ══════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await ptb_app.initialize()
    await ptb_app.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"✅ Webhook o'rnatildi: {WEBHOOK_URL}")
    asyncio.create_task(keep_alive())
    yield
    # Shutdown
    await ptb_app.shutdown()
    logger.info("🛑 Bot to'xtatildi")

web = FastAPI(lifespan=lifespan)

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
