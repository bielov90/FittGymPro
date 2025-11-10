# bot/main.py
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем токен и адрес мини-приложения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(
                text="Открыть FittGymPro 💪",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )]
        ]
    )
    await message.answer(
        "👋 Привет! Это *FittGymPro* — мини-приложение для отслеживания питания, воды и тренировок.\n\n"
        "Нажми кнопку ниже, чтобы открыть приложение:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def main():
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
