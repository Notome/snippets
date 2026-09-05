import os
import telebot
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Хранилище дедлайнов (в памяти)
deadlines = []

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
        "👋 Привет! Я бот для дедлайнов.\n\n"
        "Команды:\n"
        "add <предмет> | <дата YYYY-MM-DD> | <описание>\n"
        "list — показать дедлайны\n"
        "del <номер> — удалить дедлайн"
    )

# Добавление дедлайна
@bot.message_handler(func=lambda msg: msg.text.startswith("add"))
def add_deadline(message):
    try:
        _, data = message.text.split(" ", 1)
        subject, date_str, desc = [x.strip() for x in data.split("|")]

        date = datetime.strptime(date_str, "%Y-%m-%d")

        deadlines.append({
            "subject": subject,
            "date": date,
            "desc": desc
        })

        bot.send_message(message.chat.id, "✅ Дедлайн добавлен!")
    except:
        bot.send_message(message.chat.id, "❌ Ошибка формата.\nПример:\nadd История | 2026-02-20 | Реферат")

# Список дедлайнов
@bot.message_handler(commands=['list'])
def list_deadlines(message):
    if not deadlines:
        bot.send_message(message.chat.id, "📭 Нет дедлайнов")
        return

    sorted_dl = sorted(deadlines, key=lambda x: x["date"])

    text = "📚 Дедлайны:\n\n"
    for i, dl in enumerate(sorted_dl, 1):
        text += f"{i}. {dl['subject']} — {dl['date'].date()}\n{dl['desc']}\n\n"

    bot.send_message(message.chat.id, text)

# Удаление дедлайна
@bot.message_handler(func=lambda msg: msg.text.startswith("del"))
def delete_deadline(message):
    try:
        _, num = message.text.split()
        num = int(num) - 1

        sorted_dl = sorted(deadlines, key=lambda x: x["date"])
        to_delete = sorted_dl[num]

        deadlines.remove(to_delete)

        bot.send_message(message.chat.id, "🗑 Удалено")
    except:
        bot.send_message(message.chat.id, "❌ Неверный номер")

# Запуск
bot.infinity_polling()