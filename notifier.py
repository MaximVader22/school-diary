from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import new_db
import test

scheduler = AsyncIOScheduler()

async def notify(user_id):
    print("Just notified " + str(user_id) + "!")
    await test.bot.send_message(chat_id=user_id, text="Домашку делай")

def add_notifier(user_id, time):
    notify_id = "notify_" + str(user_id)

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

def remove_notifier(user_id):
    notify_id = "notify_" + str(user_id)
    scheduler.remove_job(job_id=notify_id)
    print("Removed notifier for " + str(user_id))

def initialise_all_notifiers():
    with new_db.create_connection() as client:
        users = client.execute("SELECT user_id, remind_time FROM users").fetchall()
        for user in users:
            user_id = user[0]
            time = user[1]

            if time != "":
                add_notifier(user[0], user[1])
    scheduler.start()