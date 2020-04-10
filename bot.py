from config import TOKEN
import telebot
import dbconfig
import datetime

bot = telebot.TeleBot(TOKEN)

cursor = dbconfig.db.cursor()
db = dbconfig.db    #Не самая лучшая идея

user_is_entered = False # Используется как статус юзера. Если юзер зарегистрирован, то значение будет изменено на TRUE

cursor.execute("SELECT user_id FROM users")
query_result = cursor.fetchall()    #Получаем список с элементами tuple

users_list = [ix[0] for ix in query_result]    #Генератор списка Telegram user ID, которые зарегистрированы. Надо этот момент пересмотреть.

#Расходы
costs = ['Транспорт','Питание','Продукты','Коммунальные платежи','Долги и кредиты','Развлечение','Назад']

#Доходы
incomes = ['Зарплата', 'Подработка', 'Кредит или долг', 'Депозит', 'Назад']

instruction = '''
Вот, что я умею делать:

/reg - регистрация
/cost - добавить расход
/income - добавить доход
/help - помощь
'''

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True, row_width = 1) #Клавиатура с командами
keyboard_commands.add('/reg','/help','/cost','/income')

keyboard_costs = telebot.types.ReplyKeyboardMarkup(True, row_width = 1) #Клавиатура с расходами
[keyboard_costs.add(costs[i]) for i in range(len(costs))] #Клавиатура с расходами. Не самая лучшая идея

keyboard_incomes = telebot.types.ReplyKeyboardMarkup(True, row_width = 1) #Клавиатура с доходами
[keyboard_incomes.add(incomes[i]) for i in range(len(incomes))]

@bot.message_handler(content_types = ['text'])

def get_message(message):   #Обработчик сообщений.
    
    global user_is_entered
    global users_list
    
    user_is_entered = message.from_user.id in users_list     # Проверка регистрации юзера. True - юзер уже зарегистрирован. 
    
    #Обработка команд. Хотя мне не особо нравится. Переделай потом!!! 

    if message.text == '/start':
        bot.send_message(message.chat.id, 'Добро пожаловать '+ message.from_user.first_name +' '+ message.from_user.last_name+ '! ' + instruction, reply_markup=keyboard_commands)    
    
    elif message.text == '/help': #Помощь
        bot.send_message(message.chat.id, instruction)
    
    elif message.text == '/cost': #Расход
        if user_is_entered == True:
            bot.send_message(message.chat.id, 'Выберите категорию расходов', reply_markup = keyboard_costs)
            bot.register_next_step_handler(message, add_cost)
        else:
            bot.send_message(message.chat.id, 'Вам необходимо зарегистрироватся. Для этого напишите /reg')
            
    elif message.text == '/income': #Доход
        if user_is_entered == True:
            bot.send_message(message.chat.id, 'Выберите категорию дохода', reply_markup = keyboard_incomes)
            bot.register_next_step_handler(message, add_income)
        else:
            bot.send_message(message.chat.id, 'Вам необходимо зарегистрироватся. Для этого напишите /reg')
    
    elif message.text == '/reg': #Регистрация
        if user_is_entered == True:
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы')
        else:
            bot.send_message(message.chat.id, 'Введите адрес электронной почты')    #Адрес электронной почты будет использоваться как . . . Все еще не решил)))
            bot.register_next_step_handler(message, add_user)
    else:
        bot.send_message(message.from_user.id, 'Я вас не понимаю, напишите мне /help')

def add_user(message):    #Сохрание электронной почты пользователя, и создание таблицы с именем его Telegram user ID в БД

    if message.text[0] == '/' or not (('@' in message.text) and ('.' in message.text)):  #ДОПИШИ ПРОВЕРКУ НА СУЩЕСТВОВАНИЕ ПОЧТЫ!!!
        bot.send_message(message.chat.id, 'Это не адрес электронной почты. Введите адрес электронной почты')
        bot.register_next_step_handler(message, add_user)
    
    else:
        table_name_cost = 'cost' + str(message.from_user.id)
        table_name_income = 'income' + str(message.from_user.id)
        
        try: 
            cursor.execute("""INSERT INTO users(user_id, user_email) 
                                        VALUES({user_id!r}, {user_email!r})"""
                                        .format(user_id = message.from_user.id, user_email = message.text)) #Заносим в БД Telegram user ID и email юзера
            
            cursor.execute("""CREATE TABLE {table_name}(id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, 
                                                        sum INT NOT NULL, 
                                                        CATEGORY VARCHAR(50), 
                                                        dateofentry date NOT NULL)"""
                                                        .format (table_name = table_name_cost))   #Создаем таблицу расходов
            
            cursor.execute("""CREATE TABLE {table_name}(id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, 
                                                        sum INT NOT NULL,
                                                        CATEGORY VARCHAR(50), 
                                                        dateofentry date NOT NULL)"""
                                                        .format (table_name = table_name_income))   #Создаем таблицу доходов
            db.commit()
        except:
            bot.send_message(message.chat.id, 'Не удалось зарегистрироваться. Попробуйте позднее.')
        else:
            global users_list
            users_list.append(message.from_user.id) # Добавление Telegram user ID нового юзера в список юзеров
            global user_is_entered
            user_is_entered = True
            bot.send_message(message.chat.id, 'Регистрация прошла успешна!')

    #Кажись эти функции надо бы доработать.
    #Все равно они мне не нравятся!

def add_cost(message): #Добавить расход
    
    if message.text in costs[:-1]: #Убеждаемся, что выбрана существующая категория
        category = message.text 
        bot.send_message(message.chat.id, 'Введите сумму расхода')
        bot.register_next_step_handler(message, add_to_db, 'cost', category)
    
    elif message.text == 'Назад': #Вернуться к обработчику команд
        bot.register_next_step_handler(message, get_message)
        bot.send_message(message.chat.id, 'Выберите команду', reply_markup = keyboard_commands)
    
    else: 
        bot.send_message(message.chat.id, 'Выберите категорию расхода', reply_markup = keyboard_costs)
        bot.register_next_step_handler(message, add_cost)

def add_income(message): #Добавить доход
    
    if message.text in incomes[:-1]: #Убеждаемся, что выбрана существующая категория
        category = message.text
        bot.send_message(message.chat.id, 'Введите сумму дохода')
        bot.register_next_step_handler(message, add_to_db, 'income', category)
    
    elif message.text == 'Назад': #Вернуться к обработчику команд
        bot.register_next_step_handler(message, get_message)
        bot.send_message(message.chat.id, 'Выберите команду', reply_markup = keyboard_commands)
    
    else:
        bot.send_message(message.chat.id, 'Выберите категорию дохода', reply_markup = keyboard_incomes)
        bot.register_next_step_handler(message, add_income)

def add_to_db(message, type_of_record, category): #Запись в БД.
    
    #Обработка исключений. Должно быть введено целое число
    try:
        sum_to_record = int(message.text)

    except ValueError: #Если введенное значение не число
        
        if message.text == 'Назад': #Вернуться к обработчику команд
            bot.register_next_step_handler(message, get_message)
            bot.send_message(message.chat.id, 'Выберите команду', reply_markup = keyboard_commands)
        else:
            bot.send_message(message.chat.id, 'Введите число без запятых, точек и других знаков!')
            bot.register_next_step_handler(message, add_to_db, type_of_record, category)
    
    else:
        table_name = type_of_record + str(message.from_user.id)
        today = str(datetime.date.today()) #Сегодня
        
        try: #Обработка исключений БД
            cursor.execute("""INSERT INTO {table_name}( sum,
                                                        category, 
                                                        dateofentry) 
                                                VALUES( {sum_to_record}, 
                                                        {category!r}, 
                                                        {dateofentry!r})"""
                                                .format(table_name = table_name, 
                                                        sum_to_record = sum_to_record, 
                                                        category = category,  
                                                        dateofentry = today))
            db.commit()
        except:
            bot.send_message(message.chat.id, 'Не удалось добавить запись. Попробуйте еще раз.', reply_markup = keyboard_commands)
        else:    
            
            bot.send_message(message.chat.id, 'Запись успешно добавлена', reply_markup = keyboard_commands)
            bot.register_next_step_handler(message, get_message)

bot.polling(none_stop = True)