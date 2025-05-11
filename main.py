from aiogram import Bot, Dispatcher
import asyncio

from modules import scheduler_manager
from modules.handlers import *
from modules.callback_funcs import *


# Создайте файл http_api.txt и добавьте туда токен бота (можно взять в BotFather)
with open('http_api.txt') as f:
    token = f.read().strip()

# Инициализация бота
bot = Bot(token=token)

# Последнее сообщение, отправленное пользователю
last_messages = {}

# Активация базы данных и бота
async def main():
    await bot.delete_webhook()
    init_database()
    scheduler_manager.initialise()
    await dp.start_polling(bot)

# Создание Диспетчера и добавления в него двух роутеров, асинхронный запуск бота
if __name__ == '__main__':
    dp = Dispatcher()
    dp.include_router(router_callback)
    dp.include_router(router_handler)
    asyncio.run(main())
