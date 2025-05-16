from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from modules.db_api import *


# Главное меню
def create_main_menu(user_id):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text='Профиль',
                             callback_data='profile'),
        InlineKeyboardButton(text='Расписание',
                             callback_data='schedule'),
        InlineKeyboardButton(text='Домашнее задание',
                             callback_data='homework')
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

# Меню расписания
def create_schedule_menu(user_id):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text='Просмотреть расписание',
                             callback_data='view_schedule'),
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

# Меню профиля
def create_profile_menu():
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="Изменить время напоминания",
                             callback_data="edit_remind_time"),
        InlineKeyboardButton(text='Назад',
                             callback_data='back_to_main')
    )

    builder.adjust(1)
    return builder.as_markup()

# Меню старост
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

# Меню домашней работы
def create_homework_menu(user_id):
     builder = InlineKeyboardBuilder()
 
     builder.add(
         InlineKeyboardButton(text='Просмотреть домашнее задание', callback_data='list_homework'),
     )
 
     if has_elder_rights(user_id):
         builder.add(
             InlineKeyboardButton(text='Добавить домашнее задание', callback_data='add_homework'),
             InlineKeyboardButton(text='Удалить домашнее задание', callback_data='remove_homework'),
         )
 
     builder.row(
         InlineKeyboardButton(text='Назад',
                              callback_data='back_to_main')
     )
 
     builder.adjust(1)
     return builder.as_markup()
