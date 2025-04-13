from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
import asyncio

import notifier
import schedule_json as sch
from new_db import *

# Вставьте ваш токен вместо 'YOUR_BOT_TOKEN'
with open('http_api.txt') as f:
    token = f.read().strip()


# Состояния
class Form(StatesGroup):
    idle = State()
    edit_schedule = State()
    edit_schedule_delete = State()
    edit_schedule_add = State()
    edit_elders = State()
    edit_elders_delete = State()
    edit_elders_add = State()
    edit_remind_time = State()
    create_announcement = State()
    create_event = State()


# Глобальные переменные
json_name = 'schedule.json'

# Инициализация бота и диспетчера
bot = Bot(token=token)
dp = Dispatcher()
router = Router()
dp.include_router(router)

'''
### Кнопки ###
'''


def create_main_menu(user_id):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text='Профиль',
                             callback_data='profile'),
        InlineKeyboardButton(text='Расписание',
                             callback_data='schedule')
    )
    if is_elder(user_id) or is_admin(user_id):
        builder.add(
            InlineKeyboardButton(text='Сделать объявление', callback_data='create_announcement'),
            InlineKeyboardButton(text='Сделать объявление о мероприятии', callback_data='create_event'),
        )

    if is_admin(user_id):
        builder.add(
            InlineKeyboardButton(text='Старосты',
                                 callback_data='elders'),
        )

    builder.adjust(1)
    return builder.as_markup()


def create_schedule_menu(user_id):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text='Просмотреть расписание',
                             callback_data='view_schedule')
    )

    if has_elder_rights(user_id):
        builder.add(
            InlineKeyboardButton(text='Добавить предмет',
                                 callback_data='add_subject'),
            InlineKeyboardButton(text='Удалить предмет',
                                 callback_data='remove_subject'),
        )

    builder.row(
        InlineKeyboardButton(text='Назад',
                             callback_data='back_to_main')
    )

    builder.adjust(1)
    return builder.as_markup()


def create_profile_menu(user_id):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="Изменить время напоминания",
                             callback_data="edit_remind_time"),
        InlineKeyboardButton(text='Назад',
                             callback_data='back_to_main')
    )

    builder.adjust(1)
    return builder.as_markup()


def create_elders_menu(user_id):
    builder = InlineKeyboardBuilder()

    if is_admin(user_id):
        builder.add(
            InlineKeyboardButton(text='Добавить старосту',
                                 callback_data='add_elder'),
            InlineKeyboardButton(text='Удалить старосту',
                                 callback_data='remove_elder'),
        )

    builder.row(
        InlineKeyboardButton(text='Назад',
                             callback_data='back_to_main')
    )

    builder.adjust(1)
    return builder.as_markup()


# Обработчик команды /start
@router.message(Command("start"))
async def send_welcome(message: Message, state: FSMContext):
    create_user(message.from_user.id, None, is_admin=are_users_empty())
    set_username(message.from_user.id, message.from_user.username)
    await state.set_state(Form.idle)
    await message.answer("Приветствую! Используйте кнопки для навигации.",
                         reply_markup=create_main_menu(message.from_user.id))


'''
### Callback-функции ###
'''


# Профиль
@router.callback_query(F.data == "profile")
async def profile(call: CallbackQuery):
    await call.answer()
    await call.message.answer("Это ваш профиль. Здесь пока ничего нет.",
                              reply_markup=create_profile_menu(call.from_user.id))


# Расписание
@router.callback_query(F.data == "schedule", StateFilter(Form.idle))
async def schedule(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule)
    await call.message.answer("Выберите действие:",
                              reply_markup=create_schedule_menu(call.from_user.id))


# Старосты
@router.callback_query(F.data == "elders", StateFilter(Form.idle))
async def elders(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders)
    await call.message.answer("Выберите действие:",
                              reply_markup=create_elders_menu(call.from_user.id))


# Просмотр расписания
@router.callback_query(F.data == "view_schedule")
async def view_schedule(call: CallbackQuery):
    await call.answer()

    schedule_data = sch.load_schedule(json_name)

    if not schedule_data:
        await call.message.answer("Расписание пустое.")
        return

    response = "Ваше текущее расписание:\n"

    for day, lessons in schedule_data.items():
        response += f"{day}:\n"
        for lesson in lessons:
            response += f'{lesson["name"]}: {lesson["start_time"]}-{lesson["end_time"]}\n'
        response += '\n'

    await call.message.answer(response)


# Установка времени напоминания
@router.callback_query(F.data == "edit_remind_time", StateFilter(Form.idle))
async def edit_remind_time_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_remind_time)
    await call.message.answer("Введите время напоминания в формате HH:MM :")


@router.message(F.text, StateFilter(Form.edit_remind_time))
async def handle_edit_remind_time(message: Message, state: FSMContext):
    time = message.text

    if not is_right_time_format(time):
        await message.answer(f"Укажите время в формате HH:MM.")
        return

    set_remind_time(message.from_user.id, time)
    notifier.add_notifier(message.from_user.id, time)
    await message.answer(f"Время напоминания установлено.")


# Добавление предмета
@router.callback_query(F.data == "add_subject")
async def add_subject_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule_add)
    await call.message.answer(
        "Введите день недели, предмет, время начала и время конца через запятую (например: `Monday, Math, 8:30, 9:10`):")


@router.message(F.text, StateFilter(Form.edit_schedule_add))
async def handle_add_subject(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("У вас нет прав старосты.")
        return
    try:
        day, subject, start_time, end_time = map(str.strip, message.text.split(',', 3))

        if not is_right_time_format(start_time) or not is_right_time_format(end_time):
            await message.answer("Неверный формат ввода времени: HH:MM")
            return

        sch.add_schedule(json_name, day, subject, start_time, end_time)
        await message.answer(f"Предмет '{subject}' успешно добавлен на {day}.")
    except ValueError:
        await message.answer("Неверный формат ввода. Пожалуйста, используйте формат: день, предмет.")


# Удаление предмета
@router.callback_query(F.data == "remove_subject")
async def remove_subject_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_schedule_delete)
    await call.message.answer("Введите название предмета для удаления:")


@router.message(F.text, StateFilter(Form.edit_schedule_delete))
async def handle_remove_subject(message: Message, state: FSMContext):
    if not has_elder_rights(message.from_user.id):
        await message.answer("У вас нет прав старосты.")
        return

    subject = message.text.strip()
    sch.remove_one_subject(json_name, subject)
    await message.answer(f"Попытка удалить предмет '{subject}' завершена.")


# Добавление старосты
@router.callback_query(F.data == "add_elder")
async def add_elder_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders_add)
    await call.message.answer("Введите имя пользователя нового старосты:")


@router.message(F.text, StateFilter(Form.edit_elders_add))
async def handle_add_elder(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора.")
        return

    username = message.text.strip()

    if not username_exists(username):
        await message.answer("Не найден пользователь с таким именем.")
        return

    set_elder(id_from_username(username), True)
    await message.answer(f"{username} назначен старостой.")


# Удаление старосты
@router.callback_query(F.data == "remove_elder")
async def remove_elder_prompt(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.edit_elders_delete)
    await call.message.answer("Введите имя пользователя старосты, которого надо удалить:")


@router.message(F.text, StateFilter(Form.edit_elders_delete))
async def handle_remove_elder(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("У вас нет прав администратора.")
        return

    username = message.text.strip()

    if not username_exists(username):
        await message.answer("Не найден пользователь с таким именем.")
        return

    set_elder(id_from_username(username), False)
    await message.answer(f"{username} больше не староста.")


# Создание объявления
@router.callback_query(F.data == "create_announcement")
async def create_announcement(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.create_announcement)
    await call.message.answer("Введите ваше объявление или напишите *Отмена*, если вы не хотите создавать объявление",
                              parse_mode=ParseMode.MARKDOWN_V2)


@router.message(F.text, StateFilter(Form.create_announcement))
async def handle_create_announcement(message: Message, state: FSMContext):
    await state.set_state(Form.idle)
    if message.text == "Отмена":
        await message.answer("Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
    else:
        for user_id in get_all_user_ids():
            await bot.send_message(user_id[0], message.text)
        await message.answer("Объявление создано. Вы возвращены в главное меню",
                             reply_markup=create_main_menu(message.from_user.id))


# Создание объявления о мероприятии
@router.callback_query(F.data == "create_event")
async def create_event(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.create_event)
    await call.message.answer("Введите ваше объявление в формате _Название, Время \(DD\.MM\.YYYY HH:MM\)_ или напишите *Отмена*, если вы не хотите создавать объявление", parse_mode=ParseMode.MARKDOWN_V2)


@router.message(F.text, StateFilter(Form.create_event))
async def handle_create_event(message: Message, state: FSMContext):
    if message.text == "Отмена":
            await message.answer("Вы возвращены в главное меню", reply_markup=create_main_menu(message.from_user.id))
    elif len(message.text) > 18 and is_right_date_format(message.text[-16:]):
        await state.set_state(Form.idle)
        for user_id in get_all_user_ids():
            await bot.send_message(user_id[0], message.text)
        await message.answer("Объявление создано. Вы возвращены в главное меню",
                             reply_markup=create_main_menu(message.from_user.id))
    else:
        await message.answer("Неправильный формат сообщения")


# В главное меню
@router.callback_query(F.data == "back_to_main")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.set_state(Form.idle)
    await call.message.answer("Вы вернулись в главное меню.",
                              reply_markup=create_main_menu(call.from_user.id))


'''
### MAIN-функция ###
### Запуск бота ###
'''


async def main():
    await bot.delete_webhook()
    init_database()
    notifier.initialise_all_notifiers()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
