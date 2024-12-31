from datetime import datetime
import telebot, time
from db_api import *

WEEKDAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

with open('http_api.txt') as f:
    bot = telebot.TeleBot(f.read())

@bot.message_handler(commands=['start'])
def start(message):
    create_user(message.chat.username, is_admin=True) # TODO первый пользователь админ, админ может присваивать статус админа другим пользователям
    update_user_state(message.chat.username, "idle")
    bot.send_message(message.chat.id, 'Приветсвуем Вас в нашем боте. Используйте команды из меню для навигации.', reply_markup=telebot.types.ReplyKeyboardRemove())

def idle(message):
    # TODO отредактировать текста сообщений, чтобы они оказались адекватными
    bot.send_message(message.chat.id, 'Используйте команды из меню для навигации.', reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(commands=['status'])
def status(message):
    update_user_state(message.chat.username, "idle")
    weekday = WEEKDAYS[datetime.weekday(datetime.fromtimestamp(time.mktime(time.localtime(message.date))))]
    now = datetime.fromtimestamp(time.mktime(time.localtime(message.date)))
    bot.send_message(message.chat.id, now, reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):
    state = get_user_state(message.chat.username)
    if state == 'idle':
        idle(message)

if __name__ == '__main__':
    init_database()
    bot.infinity_polling()
