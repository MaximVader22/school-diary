from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules import notifier
from modules import db_api
from datetime import datetime


scheduler = AsyncIOScheduler() # Общий экземпляр AsyncIOScheduler для всех модулей


# Инициализация всех модулей и задач, связанных с apscheduler
def initialise():
    notifier.initialise()
    scheduler.add_job(clean_homework, 'interval', id="clean_homework", hours=1)


# Очитска просроченных домашних заданий
def clean_homework():
    print("Cleaning homework")
    homework_list = db_api.list_homework()

    for work in homework_list:
        expires = datetime.strptime(work[3], "%d.%m.%Y").date()
        today = datetime.today().date()

        if today > expires:
            print(f"Homework {work[0]} was deleted while cleaning.")
            db_api.remove_homework(work[0])


def add_event_notifications(text: str, time: datetime):
    pass
