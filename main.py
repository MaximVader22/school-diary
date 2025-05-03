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
dp.include_router(router) 
dp.include_router(router2)

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

# Обработка изображений для домашнего задания
@router2.message(F.photo, StateFilter(Form.edit_homework_add))
async def handle_add_homework_image(message: Message, state: FSMContext):
    max_photos = 10 # Максимальное количество фото в одной домашке
 
    data = await state.get_data()
    current_photos = data.get("photos", [])
 
    best_photos = [message.photo[-1]] # Получение только версий изображения с самым высоким качеством
    photos_in_message = len(best_photos)
    free_photos_space = min(len(message.photo), max_photos - len(current_photos)) # Сколько фото ещё можно добавить
 
    if free_photos_space <= 0:
        await message.answer(f"Вы не можете прикрепить более {max_photos} изображений.")
        return
 
    photos = []
 
    for photo in best_photos[:photos_in_message]:
        photo_file = await bot.get_file(photo.file_id)
        downloaded_file = await bot.download_file(photo_file.file_path)
        binary_data = downloaded_file.read()
        photos.append(binary_data)
 
    updated_photos = current_photos + photos
 
    await state.update_data({"photos": updated_photos})
    await message.answer("Фотография была добавлена.")

async def main():
    await bot.delete_webhook()
    init_database()
    notifier.initialise_all_notifiers()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
