from config import TOKEN
import telebot
import dbconfig

bot = telebot.TeleBot(TOKEN)

cursor = dbconfig.db.cursor()
db = dbconfig.db    #Не самая лучшая идея

user_id = 0
user_email = 'username'

instruction = '''
Вот что я умею:

/reg - Зарегистриваться как новый пользователь. Все ваши данные будут удалены.
/enter - вход
/help - помощь

'''

@bot.message_handler(content_types = ['text'])

def get_message(message):   #Обработчик сообщений.
    
    if message.text == '/start':
        pass
    
    elif message.text == '/help':
        bot.send_message(message.chat.id, instruction)
    
    elif message.text == '/reg':
        global user_id
        user_id = message.from_user.id      #Получение Telegram user ID
        bot.send_message(message.chat.id, 'Введите адрес электронной почты')    #Адрес электронной почты будет использоваться в качестве логина
        bot.register_next_step_handler(message, add_user_email)
    
    elif message.text == '/enter':
        pass

    
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю, напиши мне /help')

def add_user_email(message):    #Добавление электронной почты пользователя 
    
    global user_email
    global user_id
    user_email = message.text
    cursor.execute("INSERT INTO users(user_id, user_email) VALUES(%s, %r)" %(user_id, user_email))  #Заносим в БД Telegram user ID и email юзера
    db.commit()

bot.polling(none_stop= True)