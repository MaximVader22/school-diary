import telebot

bot = telebot.TeleBot('6239222419:AAGLnp1mJXfKllPTNmq9oFo4tWdoI6WR4_A')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, message.text)

if __name__ == '__main__':
     bot.infinity_polling()