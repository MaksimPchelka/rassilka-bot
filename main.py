# тут уже бд так шо загрузить на фри тарифе в bothost.ru не получится

import asyncio
import sqlite3
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramForbiddenError

TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN") or "8381940337:AAFg7H4y-NmZTbca7mtLsJVWvvoxOViqoYc"
ADMIN_ID = 7179906538

bot = Bot(token=TOKEN)
dp = Dispatcher()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]

@dp.message(Command("start"))
async def cmd_start(message: Message):
    add_user(message.from_user.id)
    await message.answer("Жди рассылки")

@dp.message(Command("stats"), F.from_user.id == ADMIN_ID)
async def cmd_stats(message: Message):
    users = get_all_users()
    await message.answer(f"📊 Всего пользователей в базе: **{len(users)}**", parse_mode="Markdown")

@dp.message(Command("send"), F.from_user.id == ADMIN_ID)
async def cmd_broadcast(message: Message):
    broadcast_text = message.text[6:].strip()
    
    if not broadcast_text:
        await message.answer("❌ Введите текст рассылки после команды. Пример: `/send Всем привет`")
        return

    users = get_all_users()
    count = 0
    blocked = 0

    status_msg = await message.answer(f"🚀 Начинаю рассылку на {len(users)} человек(-а)")

    for user_id in users:
        try:
            await bot.send_message(user_id, broadcast_text)
            count += 1
            await asyncio.sleep(0.05)
        except TelegramForbiddenError:
            blocked += 1
        except Exception as e:
            print(f"Ошибка при отправке {user_id}: {e}")

    await status_msg.edit_text(
        f"✅ **Рассылка завершена**\n\n"
        f"📥 Доставлено: {count}\n"
        f"🚫 Заблокировали бота: {blocked}",
        parse_mode="Markdown"
    )

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())