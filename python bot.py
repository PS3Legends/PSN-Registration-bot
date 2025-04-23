from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import json
import re

TOKEN = "YOUR_BOT_TOKEN"
DATA_FILE = 'players.json'

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_user_psns(data, user_id):
    return data.get(str(user_id), {}).get('psns', [])

def psn_exists(data, psn_id):
    for user_data in data.values():
        if psn_id in user_data.get('psns', []):
            return True
    return False

async def start(update: Update, context):
    await update.message.reply_text("مرحبًا! استخدم /psn لتسجيل معرفات PSN الخاصة بك.")

async def register_id(update: Update, context):
    user_id = update.message.from_user.id
    psn_id = update.message.text.split()[1] if len(update.message.text.split()) > 1 else None
    if not psn_id or not re.match(r"^[A-Za-z0-9_]{3,16}$", psn_id):
        await update.message.reply_text("الرجاء إدخال معرف PSN صالح.")
        return

    data = load_json(DATA_FILE)
    if not psn_exists(data, psn_id):
        if str(user_id) not in data:
            data[str(user_id)] = {'psns': []}
        data[str(user_id)]['psns'].append(psn_id)
        save_json(DATA_FILE, data)
        await update.message.reply_text(f"تم تسجيل معرف PSN: {psn_id}")
    else:
        await update.message.reply_text("هذا المعرف موجود بالفعل!")

async def list_games(update: Update, context):
    user_id = update.message.from_user.id
    data = load_json(DATA_FILE)
    psns = get_user_psns(data, user_id)
    
    if psns:
        await update.message.reply_text("معرفات PSN المسجلة: " + ", ".join(psns))
    else:
        await update.message.reply_text("لم تقم بتسجيل أي معرف PSN بعد.")

async def reset_data(update: Update, context):
    data = load_json(DATA_FILE)
    data.clear()
    save_json(DATA_FILE, data)
    await update.message.reply_text("تم إعادة جميع البيانات.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("psn", register_id))
    app.add_handler(CommandHandler("list", list_games))
    app.add_handler(CommandHandler("reset", reset_data))

    app.run_polling()

if __name__ == "__main__":
    main()
