import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)

ADMIN_IDS = [123456789]  # استبدل هذا بالـ user_id الخاص بك

data = {
    "Surgery": [f"Chapter {i+1}" for i in range(20)],
    "Internal Medicine": [f"Chapter {i+1}" for i in range(20)],
    "Neurology": [f"Chapter {i+1}" for i in range(20)],
    "Psychology": [f"Chapter {i+1}" for i in range(20)],
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        buttons = [
            [InlineKeyboardButton("📂 إدارة المواد", callback_data="admin_subjects")],
            [InlineKeyboardButton("⚙️ إعدادات البوت", callback_data="admin_settings")],
        ]
        await update.message.reply_text("مرحباً أيها المدير 👨‍⚕️", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        buttons = [[InlineKeyboardButton(subject, callback_data=f"subject|{subject}")]
                   for subject in data]
        await update.message.reply_text("اختر المادة:", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("subject|"):
        subject = query.data.split("|")[1]
        chapters = data.get(subject, [])
        buttons = [[InlineKeyboardButton(ch, callback_data=f"chapter|{subject}|{ch}")]
                   for ch in chapters]
        await query.edit_message_text(f"{subject} - الشباتر:", reply_markup=InlineKeyboardMarkup(buttons))
    elif query.data.startswith("chapter|"):
        _, subject, chapter = query.data.split("|")
        await query.edit_message_text(f"{subject} - {chapter}:
📄 هذا ملخص تجريبي.")
    elif query.data == "admin_subjects":
        await query.edit_message_text("📂 إدارة المواد (تجريبي)")
    elif query.data == "admin_settings":
        await query.edit_message_text("⚙️ إعدادات البوت (تجريبي)")

if __name__ == '__main__':
    TOKEN = os.environ.get("API_TOKEN", "PUT-YOUR-TOKEN-HERE")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.run_polling()