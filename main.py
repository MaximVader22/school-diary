from aiogram import Bot, Dispatcher, Router
from modules.db_api import *
import modules.notifier as notifier
import asyncio

from modules.handlers import *
from modules.callback_funcs import *

# Вставьте ваш токен вместо 'YOUR_BOT_TOKEN'
with open('http_api.txt') as f:
    token = f.read().strip()

# Инициализация бота и диспетчера
bot = Bot(token=token)
dp = Dispatcher()

@router.message(F.text, StateFilter(Form.create_announcement))
async def handle_create_announcement(message: Message, state: FSMContext):
    await state.set_state(Form.idle)
    if not has_elder_rights(message.from_user.id):
        await message.answer("У вас нет прав для этого.")
    elif message.text == "Отмена":
        await message.answer("Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
    else:
        for user_id in get_all_user_ids():
            await bot.send_message(user_id[0], message.text)
        await message.answer("Объявление создано. Вы возвращены в главное меню",
                             reply_markup=create_main_menu(message.from_user.id))



@router.message(F.text, StateFilter(Form.create_event))
async def handle_create_event(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("У вас нет прав для этого.")
    elif message.text == "Отмена":
            await message.answer("Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
    elif len(message.text) > 18 and is_right_date_format(message.text[-16:]):
        await state.set_state(Form.idle)
        for user_id in get_all_user_ids():
            await bot.send_message(user_id[0], message.text)
        await message.answer("Объявление создано. Вы возвращены в главное меню",
                             reply_markup=create_main_menu(message.from_user.id))
    else:
        await message.answer("Неправильный формат сообщения")

async def main():
    await bot.delete_webhook()
    init_database()
    notifier.initialise_all_notifiers()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())