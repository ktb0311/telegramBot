from config import TOKEN
import telebot

instruction = '''
'Напиши Привет'
'''
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types = ['text'])

def get_text_messages(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Привет! Чем я могу помощь?')
    elif message.text == 'Привет':
        bot.send_message(message.from_user.id, 'Привет еще раз')
    elif message.text == '/help':
        bot.send_message(message.from_user.id, instruction)
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю, напиши мне /help')

bot.polling(none_stop= True, interval = 0)