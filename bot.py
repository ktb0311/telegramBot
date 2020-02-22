from config import TOKEN
import telebot

instruction = '''
Вот что я умею:

/reg - регистрация
/enter - вход
/help - помощь
'''
bot = telebot.TeleBot(TOKEN)

name = 'name'
surname = 'surname'
dob = '01.01.2000' # Date of birth - дата рождения

@bot.message_handler(content_types = ['text'])

def get_message(message):   #Обработчик сообщений.
    if message.text == '/start':
        bot.send_message(message.chat.id ,'Привет!' + instruction)
    elif message.text == '/help':
        bot.send_message(message.chat.id, instruction)
    elif message.text == '/reg':
        bot.send_message(message.chat.id, 'Введите ваше имя')
        bot.register_next_step_handler(message, add_name)
    elif message.text == '/enter':
        bot.send_message(message.chat.id, name + ' ' + surname + ' родился в ' + dob)
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю, напиши мне /help')

def add_name(message):  #Добавить имя.
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Введите вашу фамилию')
    bot.register_next_step_handler(message, add_surname)

def add_surname(message): #Добавить фамилию.
    global surname
    surname = message.text
    bot.send_message(message.chat.id, 'Введите дату рождения в следующем формате: 31.12.1993')
    bot.register_next_step_handler(message, add_dob)

def add_dob(message): #Добавить дату рождения.
    global dob
    dob = message.text

bot.polling(none_stop= True, interval = 0)