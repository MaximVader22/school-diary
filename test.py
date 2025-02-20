from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# Вставьте ваш токен вместо 'YOUR_BOT_TOKEN'
with open('http_api.txt') as f:
    token=f.read()

# Инициализация бота и диспетчера
bot = Bot(token=token)
dp = Dispatcher()
builder = InlineKeyboardBuilder()

# Создаем роутер
router = Router()
dp.include_router(router)

def create_button_start():
    builder.add(InlineKeyboardButton(text='Профиль', callback_data='profile'))
    builder.adjust(1)
    return builder.as_markup()
    

# Обработчик команды /start
@router.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Приветствую! Используйте кнопки для навигации.", reply_markup=create_button_start())
    
    

#callback-функции
@router.callback_query(F.data.startswith('profile'))
async def profile(call: CallbackQuery):
    pass

# Запуск бота
async def main():
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
