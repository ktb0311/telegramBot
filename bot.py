from config import TOKEN
import telebot

instruction = '''
Вот что я умею:

/reg - Зарегистриваться как новый пользователь. Все ваши данные будут удалены.
/enter - вход
/help - помощь

'''
bot = telebot.TeleBot(TOKEN)

user_id = 'id'
user_email = 'username'
nursik = 440165562
ela = 558589609
rambo = 463863602
creator = 342541293

@bot.message_handler(content_types = ['text'])

def get_message(message):   #Обработчик сообщений.
    
    if message.text == '/start':
        
        if message.from_user.id == creator:
            bot.send_message(message.chat.id ,'Здравствуй! Великий создатель! ' + instruction)
        if message.from_user.id == nursik:
            bot.send_message(message.chat.id ,'Привет Нурсик!' + instruction)
        if message.from_user.id == ela:
            bot.send_message(message.chat.id ,'Привет Ела!' + instruction)
        if message.from_user.id == rambo:
            bot.send_message(message.chat.id ,'Привет Рая!' + instruction)
    
    elif message.text == '/help':
        bot.send_message(message.chat.id, instruction)
    
    elif message.text == '/reg':
        global user_id
        user_id = message.from_user.id #Получение telegram user id
        bot.send_message(message.chat.id, 'Введите адрес электронной почты')    #Адрес электронной почты будет использоваться в качестве логина
        bot.register_next_step_handler(message, add_user_email)
    
    elif message.text == '/enter':
        bot.send_message(message.chat.id, user_id)
    
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю, напиши мне /help')

def add_user_email(message): #Добавление электронной почты пользователя 
    
    global user_email
    user_email = message.text

bot.polling(none_stop= True, interval = 0)