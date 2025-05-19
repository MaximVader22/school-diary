from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.triggers.cron import CronTrigger
import modules.db_api as db_api

import main
from modules import scheduler_manager


# Активация напоминалки
async def notify(user_id):
    print("Just notified " + str(user_id) + "!")
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Просмотреть домашнее задание", callback_data="list_homework"))

    await main.bot.send_message(chat_id=user_id, text="""
⏱️ Напоминаем вам о выполнении вашего домашнего задания
    """, reply_markup=builder.as_markup())

# Доавбление напоминалки
def add_notifier(user_id, time):
    notify_id = "notify_" + str(user_id)
    scheduler = scheduler_manager.scheduler

    if scheduler.get_job(job_id=notify_id):
        scheduler.remove_job(job_id=notify_id)
        print("Removed previous notifier for " + str(user_id))
    print("Added notifier for " + str(user_id) + " in " + time)
    time_split = time.split(":")
    hour = time_split[0]
    minute = time_split[1]
    trigger = CronTrigger(
        year="*", month="*", day="*", hour=hour, minute=minute, second="0"
    )
    scheduler.add_job(notify, id = notify_id, trigger=trigger, args=[user_id])

# Удаление напоминалки
def remove_notifier(user_id):
    notify_id = "notify_" + str(user_id)
    scheduler_manager.scheduler.remove_job(job_id=notify_id)
    print("Removed notifier for " + str(user_id))

# Инициализация напоминалки
def initialise():
    with db_api.create_connection() as client:
        users = client.execute("SELECT user_id, remind_time FROM users").fetchall()
        for user in users:
            user_id = user[0]
            time = user[1]

            if time != "":
                add_notifier(user[0], user[1])
    scheduler_manager.scheduler.start()
