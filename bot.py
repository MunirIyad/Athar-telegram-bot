import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

# المعرفات المسموح لها بالإدارة
ADMIN_IDS = [1195052497]

# البيانات التجريبية
data = {
    "Surgery": [f"Chapter {i+1}" for i in range(3)],
    "Internal Medicine": [f"Chapter {i+1}" for i in range(3)],
    "Neurology": [f"Chapter {i+1}" for i in range(3)],
    "Psychology": [f"Chapter {i+1}" for i in range(3)],
}

user_state = {}  # لحفظ حالة المستخدم

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 المواد الطبية", callback_data="list_subjects")],
        [InlineKeyboardButton("🛠️ إدارة المواد", callback_data="admin_menu")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك في البوت الطبي!", reply_markup=main_menu_keyboard())

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "list_subjects":
        keyboard = [[InlineKeyboardButton(subject, callback_data=f"subject|{subject}")] for subject in data]
        keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="main")])
        await query.edit_message_text("اختر المادة:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("subject|"):
        subject = query.data.split("|")[1]
        keyboard = [[InlineKeyboardButton(ch, callback_data=f"chapter|{subject}|{ch}")]
                    for ch in data.get(subject, [])]
        keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="list_subjects")])
        await query.edit_message_text(f"{subject} - الشباتر:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("chapter|"):
        _, subject, chapter = query.data.split("|")
        keyboard = [[InlineKeyboardButton("⬅️ رجوع", callback_data=f"subject|{subject}")]]
        await query.edit_message_text(f"{subject} - {chapter}:\n📄 هذا ملخص تجريبي.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "main":
        await query.edit_message_text("القائمة الرئيسية:", reply_markup=main_menu_keyboard())

    elif query.data == "admin_menu" and user_id in ADMIN_IDS:
        keyboard = [
            [InlineKeyboardButton("➕ إضافة مادة", callback_data="add_subject")],
            [InlineKeyboardButton("📁 تعديل المواد", callback_data="edit_subjects")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="main")]
        ]
        await query.edit_message_text("لوحة تحكم الأدمن:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "add_subject" and user_id in ADMIN_IDS:
        user_state[user_id] = "awaiting_subject_name"
        await query.edit_message_text("أرسل اسم المادة الجديدة:")

    elif query.data == "edit_subjects" and user_id in ADMIN_IDS:
        keyboard = [[InlineKeyboardButton(f"✏️ {s}", callback_data=f"edit_subject|{s}")] for s in data]
        keyboard.append([InlineKeyboardButton("⬅️ رجوع", callback_data="admin_menu")])
        await query.edit_message_text("اختر المادة للتعديل:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("edit_subject|") and user_id in ADMIN_IDS:
        subject = query.data.split("|")[1]
        keyboard = [
            [InlineKeyboardButton("➕ إضافة شابتر", callback_data=f"add_chapter|{subject}")],
            [InlineKeyboardButton("🗑️ حذف المادة", callback_data=f"delete_subject|{subject}")],
            [InlineKeyboardButton("⬅️ رجوع", callback_data="edit_subjects")]
        ]
        await query.edit_message_text(f"إدارة المادة: {subject}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("add_chapter|") and user_id in ADMIN_IDS:
        subject = query.data.split("|")[1]
        user_state[user_id] = f"awaiting_chapter_name|{subject}"
        await query.edit_message_text(f"أرسل اسم الشابتر الجديد لإضافته إلى {subject}:")

    elif query.data.startswith("delete_subject|") and user_id in ADMIN_IDS:
        subject = query.data.split("|")[1]
        data.pop(subject, None)
        await query.edit_message_text(f"✅ تم حذف المادة: {subject}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in ADMIN_IDS and user_id in user_state:
        state = user_state.pop(user_id)
        if state == "awaiting_subject_name":
            data[text] = []
            await update.message.reply_text(f"✅ تم إضافة المادة: {text}", reply_markup=main_menu_keyboard())
        elif state.startswith("awaiting_chapter_name|"):
            subject = state.split("|")[1]
            if subject in data:
                data[subject].append(text)
                await update.message.reply_text(f"✅ تم إضافة الشابتر: {text} إلى {subject}", reply_markup=main_menu_keyboard())

# تشغيل البوت
if __name__ == '__main__':
    TOKEN = os.environ.get("API_TOKEN", "8089864249:AAFitTjy7KMKGXBFaunnuc-_so67-vLKgxo")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
