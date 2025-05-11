from aiogram import Router
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F, types

import main
from modules.FSM_states import *
from modules.create_menu import *
import modules.schedule_json as sch
import modules.notifier as notifier


router_handler = Router()

DAYS_OF_WEEK = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')


# Обработчик команды /start
@router_handler.message(Command("start"))
async def send_welcome(message: Message, state: FSMContext):
    create_user(message.from_user.id, None, is_admin=are_users_empty())
    set_username(message.from_user.id, message.from_user.username)
    await state.set_state(Form.idle)
    await message.answer("Приветствую! Используйте кнопки для навигации:",
                         reply_markup=create_main_menu(message.from_user.id))

# Обработчик изменения напоминалки
@router_handler.message(F.text, StateFilter(Form.edit_remind_time))
async def handle_edit_remind_time(message: Message, state: FSMContext):
    text = message.text

    if text == "Удалить":
        await message.answer(f"✅ Время напоминания удалено. Вы возвращены в профиль", reply_markup=create_profile_menu())
        set_remind_time(message.from_user.id, None)
        notifier.remove_notifier(message.from_user.id)
        await state.set_state(Form.idle)
        return

    if not is_right_time_format(text):
        await message.answer(f"❌ Укажите время в формате HH:MM")
        return

    set_remind_time(message.from_user.id, text)
    notifier.add_notifier(message.from_user.id, text)
    await state.set_state(Form.idle)
    await message.answer(f"✅ Время напоминания установлено. Вы возвращены в профиль", reply_markup=create_profile_menu())

# Обработчик добавления предмета
@router_handler.message(F.text, StateFilter(Form.edit_schedule_add))
async def handle_add_subject(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("❌ У вас нет прав старосты")
        return
    try:
        if message.text == "Отмена":
            await state.set_state(Form.idle)
            await message.answer("❌ Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
            return

        await message.delete()

        day, subject, start_time, end_time = map(str.strip, message.text.split(',', 3))
        assert day in DAYS_OF_WEEK

        if not is_right_time_format(start_time) or not is_right_time_format(end_time):
            await message.answer("❌ Неверный формат ввода времени: HH:MM")
            return

        sch.add_schedule('schedule.json', day, subject, start_time, end_time)
        await message.answer(f"✅ Предмет '{subject}' успешно добавлен на {day}")
    except ValueError:
        await message.answer("❌ Неверный формат ввода. Пожалуйста, используйте формат: день недели, предмет, время начала урока, время конца урока (время в формате ЧЧ:ММ)")
    except AssertionError:
        await message.answer("❌ Неверный формат ввода дня недели")

# Обработчик удаления предмета
@router_handler.message(F.text, StateFilter(Form.edit_schedule_delete))
async def handle_remove_subject(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("❌ У вас нет прав старосты")
        return

    subject = message.text.strip()
    sch.remove_one_subject('schedule.json', subject)
    await message.answer(f"✅ Попытка удалить предмет '{subject}' завершена")

# Обработчик добавления старосты
@router_handler.message(F.text, StateFilter(Form.edit_elders_add))
async def handle_add_elder(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return

    username = message.text.strip()
    if username[0] == '@':
        username = username[1:]

    if not username_exists(username):
        await message.answer("❌ Не найден пользователь с таким именем")
        return

    set_elder(username, True)
    print(f"Added elder {username}")
    await message.answer(f"✅ {username} назначен старостой")

# Обработчик удаления старосты
@router_handler.message(F.text, StateFilter(Form.edit_elders_delete))
async def handle_remove_elder(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return

    username = message.text.strip()
    if username[0] == '@':
        username = username[1:]

    if not username_exists(username):
        await message.answer("❌ Не найден пользователь с таким именем")
        return

    set_elder(id_from_username(username), False)
    print(f"Removed elder {username}")
    await message.answer(f"✅ {username} больше не староста")

# Обработчик создания объявления
@router_handler.message(F.text, StateFilter(Form.create_announcement))
async def handle_create_announcement(message: Message, state: FSMContext):
    await state.set_state(Form.idle)
    if not has_elder_rights(message.from_user.id):
        await message.answer("❌ У вас нет прав для этого")
    elif message.text == "Отмена":
        await message.answer("Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
    else:
        announcement = f'Объявление от пользователя @{message.from_user.username}:\n\n{message.text}'
        for user_id in get_all_user_ids():
            await main.bot.send_message(user_id[0], announcement)
        await message.answer("✅ Объявление создано. Вы возвращены в главное меню",
                             reply_markup=create_main_menu(message.from_user.id))

# Обработчик создания объявления о мероприятии
@router_handler.message(F.text, StateFilter(Form.create_event))
async def handle_create_event(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await state.set_state(Form.idle)
        await message.answer("❌ У вас нет прав для этого")
    elif message.text == "Отмена":
        await state.set_state(Form.idle)
        await message.answer("Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
    elif len(message.text) > 20 and is_right_date_format(message.text[-16:]):
        await state.set_state(Form.idle)
        announcement = f'Объявление о мероприятии от пользователя @{message.from_user.username}:\n\n{message.text[:-18]}\n\nВремя события: {message.text[-16:]}'
        for user_id in get_all_user_ids():
            await main.bot.send_message(user_id[0], announcement)
        await message.answer("✅ Объявление создано. Вы возвращены в главное меню",
                             reply_markup=create_main_menu(message.from_user.id))
    else:
        await message.answer("❌ Неправильный формат сообщения")

# Обработчик добавления домашней работы
@router_handler.message(F.text, StateFilter(Form.edit_homework_add))
async def handle_add_homework(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer("Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
        return

    content = message.text.split(";")
 
    if len(content) != 3:
        await message.answer("❌ Неверное количество аргументов")
        return
 
    date = content[0]
    subject = content[1]
    description = content[2]
 
    if not is_right_homework_date_format(date):
        await message.answer("❌ Неверный формат даты")
        return
 
    data = await state.get_data()
    photos = data.get("photos", [])
 
    add_homework(date, subject, description, photos)
 
    await message.answer(f"✅ Домашнее задание было добавлено")
    await state.clear()

# Обработчик изображений для домашнего задания
@router_handler.message(F.photo, StateFilter(Form.edit_homework_add))
async def handle_add_homework_image(message: Message, state: FSMContext):
    max_photos = 10 # Максимальное количество фото в одной домашке
 
    data = await state.get_data()
    current_photos = data.get("photos", [])
 
    best_photos = [message.photo[-1]] # Получение только версий изображения с самым высоким качеством
    photos_in_message = len(best_photos)
    free_photos_space = min(len(message.photo), max_photos - len(current_photos)) # Сколько фото ещё можно добавить
 
    if free_photos_space <= 0:
        await message.answer(f"❌ Вы не можете прикрепить более {max_photos} изображений")
        return
 
    photos = []
 
    for photo in best_photos[:photos_in_message]:
        photo_file = await main.bot.get_file(photo.file_id)
        downloaded_file = await main.bot.download_file(photo_file.file_path)
        binary_data = downloaded_file.read()
        photos.append(binary_data)
 
    updated_photos = current_photos + photos
 
    await state.update_data({"photos": updated_photos})
    await message.answer("✅ Фотография была добавлена")

# Обработчик нераспознанного запроса:
@router_handler.message()
async def idle(message: types.Message, state: FSMContext):
    await state.set_state(Form.idle)
    await message.answer("Команда не понята. Используйте кнопки для навигации:",
                         reply_markup=create_main_menu(message.from_user.id))
