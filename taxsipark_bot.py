"""
🚖 TaxsiPark Telegram Bot
"""

import logging
import os
import asyncio
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
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ══════════════════════════════════════════
#            SOZLAMALAR
# ══════════════════════════════════════════

# Tokeningizga tegmadim, o'z holicha qoldi
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
#            KLAVIATURALAR
# ══════════════════════════════════════════

def kb_start():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("🚀 START")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def kb_phone():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni avtomatik yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def kb_main():
    return ReplyKeyboardMarkup(
        [
            ["🚖 TaxsiPark haqida"],
            ["📞 Bog'lanish"],
        ],
        resize_keyboard=True,
    )

def kb_taxsipark():
    return ReplyKeyboardMarkup(
        [
            ["📄 Hujjat yuborish"],
            ["ℹ️ Ma'lumot"],
            ["🔙 Orqaga"],
        ],
        resize_keyboard=True,
    )

def kb_admins():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Admin 1 (@ibrokhim_515)", url=f"https://t.me/{ADMIN_1_USERNAME}"),
        ],
        [
            InlineKeyboardButton("👤 Admin 2 (@SAFARGO_TAXI)", url=f"https://t.me/{ADMIN_2_USERNAME}"),
        ],
    ])

# ══════════════════════════════════════════
#            HANDLERS
# ══════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user

    caption = (
        f"👋 Salom, <b>{user.first_name}</b>!\n\n"
        "🚖 <b>TaxsiPark</b> botiga xush kelibsiz!\n\n"
        "Davom etish uchun <b>START</b> tugmasini bosing 👇"
    )

    try:
        if os.path.exists(WELCOME_IMAGE):
            with open(WELCOME_IMAGE, "rb") as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=kb_start(),
                )
        else:
            await update.message.reply_text(
                caption, parse_mode="HTML", reply_markup=kb_start()
            )
    except Exception as e:
        logger.error(f"Start rasm yuborishda xato: {e}")
        await update.message.reply_text(
            caption, parse_mode="HTML", reply_markup=kb_start()
        )

    return WAIT_START


async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✏️ Iltimos, <b>to'liq ismingizni</b> kiriting:\n"
        "<i>Misol: Alisher Valiyev</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True),
    )
    return ASK_NAME


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("⚠️ To'liq ismingizni kiriting.")
        return ASK_NAME

    context.user_data["name"] = name
    await update.message.reply_text(
        f"✅ Rahmat, <b>{name}</b>!\n\n"
        "📱 Endi telefon raqamingizni yuboring\n"
        "(tugma orqali yoki qo'lda +998XXXXXXXXX formatida):",
        parse_mode="HTML",
        reply_markup=kb_phone(),
    )
    return ASK_PHONE


async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith("+"):
            phone = "+" + phone
    else:
        phone = update.message.text.strip()
        if not (phone.startswith("+") and len(phone) >= 10):
            await update.message.reply_text(
                "⚠️ Noto'g'ri format. +998XXXXXXXXX shaklida kiriting:"
            )
            return ASK_PHONE

    context.user_data["phone"] = phone
    name = context.user_data.get("name", "Foydalanuvchi")

    await update.message.reply_text(
        f"🎉 <b>Ro'yxatdan o'tdingiz!</b>\n\n"
        f"👤 Ism: <b>{name}</b>\n"
        f"📱 Tel: <b>{phone}</b>\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang 👇",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )
    return MAIN_MENU


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🚖 TaxsiPark haqida":
        await update.message.reply_text(
            "🚖 <b>TaxsiPark bo'limlari:</b>\n\n"
            "📄 Hujjat yuborish — pasport va tex pasportni adminga yuboring\n"
            "ℹ️ Ma'lumot — kompaniya haqida batafsil",
            parse_mode="HTML",
            reply_markup=kb_taxsipark(),
        )
        return TAXSIPARK_MENU

    elif text == "📞 Bog'lanish":
        await update.message.reply_text(
            "📞 <b>Biz bilan bog'laning:</b>\n\n"
            "📍 Manzil: Toshkent\n"
            "📱 Telefon: +998 90 000 00 00\n"
            "🕐 Ish vaqti: 09:00 — 18:00\n\n"
            f"👤 Admin 1: @{ADMIN_1_USERNAME}\n"
            f"👤 Admin 2: @{ADMIN_2_USERNAME}",
            parse_mode="HTML",
            reply_markup=kb_main(),
        )
        return MAIN_MENU

    return MAIN_MENU


async def handle_taxsipark_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📄 Hujjat yuborish":
        await update.message.reply_text(
            "📋 <b>Pasport va Texnik pasportni adminga yuboring</b>\n\n"
            "Quyidagilardan birini tanlang:\n\n"
            "1️⃣ <b>Pasport</b> (shaxsiy)\n"
            "2️⃣ <b>Texnik pasport</b> (avtomobil)\n\n"
            "⬇️ Admin tanlang:",
            parse_mode="HTML",
            reply_markup=kb_admins(),
        )
        return TAXSIPARK_MENU

    elif text == "ℹ️ Ma'lumot":
        await update.message.reply_text(
            "🚖 <b>TaxsiPark haqida</b>\n\n"
            "• Haydovchilar uchun qulay va ishonchli platforma\n"
            "• Tez va oson ro'yxatdan o'tish\n"
            "• 24/7 qo'llab-quvvatlash xizmati\n"
            "• Toshkent va viloyatlarda faoliyat yuritadi\n\n"
            "📞 Savollar uchun adminlarga murojaat qiling.",
            parse_mode="HTML",
            reply_markup=kb_taxsipark(),
        )
        return TAXSIPARK_MENU

    elif text == "🔙 Orqaga":
        await update.message.reply_text(
            "🏠 Asosiy menyu:",
            reply_markup=kb_main(),
        )
        return MAIN_MENU

    return TAXSIPARK_MENU


async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Iltimos, menyudan tanlang yoki /start bosing."
    )


# ══════════════════════════════════════════
#            MAIN
# ══════════════════════════════════════════

def main():
    # Build application
    application = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler configuration
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            WAIT_START: [
                MessageHandler(filters.Regex("^🚀 START$"), handle_start_button)
            ],
            ASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)
            ],
            ASK_PHONE: [
                MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), handle_phone)
            ],
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
            ],
            TAXSIPARK_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_taxsipark_menu)
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            MessageHandler(filters.TEXT, fallback_handler),
        ],
    )

    application.add_handler(conv_handler)

    print("=" * 45)
    print("  🚖  TaxsiPark Bot ishga tushdi!")
    print(f"  Admin 1: @{ADMIN_1_USERNAME}")
    print(f"  Admin 2: @{ADMIN_2_USERNAME}")
    print("=" * 45)

    # run_polling ishlatishda eng xavfsiz usul
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
