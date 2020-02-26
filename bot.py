from config import TOKEN
import telebot
import dbconfig

bot = telebot.TeleBot(TOKEN)

cursor = dbconfig.db.cursor()
db = dbconfig.db    #Не самая лучшая идея

user_is_entered = False # Используется как статус юзера. Если юзер зарегистрирован, то значение будет изменено на TRUE

cursor.execute("SELECT user_id FROM users")
query_result = cursor.fetchall()    #Получаем список с элементами tuple
users_list = [ix[0] for ix in query_result]     #Создаем список Telegram user ID, которые зарегистрированы

instruction = '''
Вот что я умею делать:

/help - помощь
/new_cat - новая категория расходов
'''

@bot.message_handler(content_types = ['text'])

def get_message(message):   #Обработчик сообщений.
    
    global user_is_entered
    global users_list
    
    user_is_entered = message.from_user.id in users_list     # Изменение значение user_is_entered на True. True - юзер уже зарегистрирован. Проверка на то что юзер уже зарегистрирован
    
    if message.text == '/start':
        if user_is_entered == True: 
            bot.send_message(message.chat.id, 'Добро пожаловать '+ message.from_user.first_name +' '+ message.from_user.last_name+ '! Рад что вы вернулись.')
        else:
            bot.send_message(message.chat.id, 'Здравствуйте, ' + message.from_user.first_name +' '+ message.from_user.last_name+'! Чтобы зарегистрироваться напишите мне /reg')
        bot.send_message(message.chat.id, instruction)
    elif message.text == '/help':
        bot.send_message(message.chat.id, instruction)
    elif message.text == '/reg':
        if user_is_entered == True:    #Проверка статуса
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы')
        else:
            bot.send_message(message.chat.id, 'Введите адрес электронной почты')    #Адрес электронной почты будет использоваться как . . .
            bot.register_next_step_handler(message, add_user)
    else:
        bot.send_message(message.from_user.id, 'Я вас не понимаю, напишите мне /help')

def add_user(message):    #Сохрание электронной почты пользователя, и создание таблицы с именем его Telegram user ID в БД

    if message.text[0] == '/' or not (('@' in message.text) and ('.' in message.text)):  #ДОПИШИ ПРОВЕРКУ НА СУЩЕСТВОВАНИЕ ПОЧТЫ!!!
        bot.send_message(message.chat.id, 'Это не адрес электронной почты. Введите адрес электронной почты')
        bot.register_next_step_handler(message, add_user)
    else:
        table_name = 'user' + str(message.from_user.id)
        cursor.execute("INSERT INTO users(user_id, user_email) VALUES(%s, %r)" %(message.from_user.id, message.text))  #Заносим в БД Telegram user ID и email юзера
        cursor.execute("CREATE TABLE {table_name}(ID INT PRIMARY KEY NOT NULL, SUM INT NOT NULL, CATEGORY VARCHAR(50))".format (table_name = table_name))   #Создаем таблицы с названием user + Telegram user ID
        db.commit()
        global user_is_entered
        user_is_entered = True
        bot.send_message(message.chat.id, 'Регистрация прошла успешна!')

bot.polling(none_stop = True)