from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import asyncio
import json, os
from datetime import datetime

BOT_TOKEN = "7971083886:AAFZ8eCQRrTjaELVUDjBKD3QTqwTYlPiKuE"
CHANNEL_USERNAME = "@Premyeramultifilmlar"
ADMIN_ID = 5663190258
USERS_FILE = "users.json"

film_links = {
    str(i): f"https://t.me/Premyeramultifilmlar/{i}" for i in range(1, 1000)
}

# Foydalanuvchini saqlovchi funksiya
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_user(user_id):
    users = load_users()
    if user_id not in [u["id"] for u in users]:
        users.append({"id": user_id, "date": datetime.now().strftime("%Y-%m-%d")})
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# A'zolikni tekshirish
async def is_user_member(user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_user(user_id)

    keyboard = [
        [InlineKeyboardButton("✅ Kanalga qo‘shilish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")],
        [InlineKeyboardButton("🔁 Tekshirish", callback_data="check_membership")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Botdan foydalanish uchun kanalga a’zo bo‘ling:", reply_markup=markup)

# Tekshirish tugmasi
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if await is_user_member(user_id, context.bot):
        await query.edit_message_text("✅ Siz kanalga a’zo bo‘lgansiz. ✍️🏻 Film kodini yuboring.")
    else:
        await query.edit_message_text("❌ Kanalga a’zo emassiz.")

# Kod yuborilganda
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_user(user_id)

    if not await is_user_member(user_id, context.bot):
        keyboard = [
            [InlineKeyboardButton("✅ Kanalga qo‘shilish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")],
            [InlineKeyboardButton("🔁 Tekshirish", callback_data="check_membership")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❗ Avval kanalga a’zo bo‘ling:", reply_markup=markup)
        return

    code = update.message.text.strip()
    if code in film_links:
        await update.message.reply_text(f"🎬 Mana siz so‘ragan film:\n{film_links[code]}")
    else:
        await update.message.reply_text("❌ Bunday kodli film topilmadi.")

# Admin panel
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Ruxsat yo‘q.")
        return

    users = load_users()
    total = len(users)
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = len([u for u in users if u["date"] == today])
    last_users = [str(u["id"]) for u in users[-10:]]

    text = (
        f"👑 Admin panel\n\n"
        f"👥 Jami foydalanuvchilar: {total}\n"
        f"🆕 Bugungi yangi foydalanuvchilar: {today_count}\n"
        f"🔟 Oxirgi 10 foydalanuvchi:\n" + "\n".join(last_users) + "\n\n"
        f"✉️ Oddiy xabar yoki rasm yuborsangiz — barcha userlarga yetkaziladi."
    )
    await update.message.reply_text(text)

# Admin xabar yuborishi (broadcast)
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    users = load_users()
    count = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u["id"], text=update.message.text)
            count += 1
            await asyncio.sleep(0.1)
        except:
            continue
    await update.message.reply_text(f"✅ {count} ta foydalanuvchiga yuborildi.")

# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check_membership))
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.User(user_id=ADMIN_ID), admin_broadcast))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
app.run_polling()