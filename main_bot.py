import time

import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from os import getenv
from dotenv import load_dotenv
from DATA_changes import *

load_dotenv()
TOKEN = getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

WORLD = load_world()
users_data = load_users_data()


@bot.message_handler(commands=['help'])
def help_user(message: Message):
    bot.send_message(message.from_user.id,
                     "Если вы видите, что с ботом что-то не так, то попытайтесь использовать команду /restart. Если видите существенную ошибку, то напишите @Leoprofi")


@bot.message_handler(commands=['start', 'restart'])
def start_programm(message: Message):
    markup = ReplyKeyboardMarkup()
    user_id = str(message.from_user.id)
    with open("Media/Фоновая муза.mp3", "rb") as file:
        bot.send_audio(user_id, audio=file)
        bot.send_message(user_id, "Это фоновая музыка, если хочешь погрузиться полностью, то используй наушники")
    if user_id not in users_data:
        markup.add(KeyboardButton("Начать игру"))
        users_data[user_id] = {
            "username": message.from_user.username,
            "location_in_world": "Начальная локация",
            "user_items": [],
            "user_achievements": [],
            "user_restart_spaming": 0
        }
        savefile(users_data)
        bot.send_message(
            chat_id=user_id,
            text="Здравствуй, пользователь! Эта мелкая игра хочет показать тебе волшебный мир! Для полного погружения используй наушники (если на компе, то открой в отдельной вкладке).\n"
                 "Ну что, начинаем?)",
            reply_markup=markup,
        )
        return
    elif user_id in users_data and users_data[user_id]['location_in_world'] not in ["Начальная локация", "Сдаться"]:
        markup.add(KeyboardButton("Продолжить"), KeyboardButton("Начать заново"))

        text = f"С возвращением, {message.from_user.username}! Хочешь продолжить прохождение квеста?"
        bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=markup,
        )
        return
    else:
        markup.add(KeyboardButton("Начать игру"))
        text = f"С возвращением, {message.from_user.username}! Начинаем заново игру?"
        bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=markup,
        )
        return


def filter_continues(message):
    bottom = ["Продолжить", "Начать игру"]
    return message.text in bottom


def register_new_user(message: Message):
    users_data[str(message.from_user.id)] = {
        "username": message.from_user.username,
        "location_in_world": "Начальная локация",
        "user_items": []
    }


@bot.message_handler(func=filter_continues)
def continue_solution(message):
    user_id = str(message.from_user.id)
    send_user_location_bottoms(user_id)


def send_user_location_bottoms(user_id):
    user_location = users_data[user_id]["location_in_world"]
    image = WORLD[user_location]['img']
    bot.send_photo(
        chat_id=user_id,
        photo=open(f"Media/{image}", "rb")
    )
    markup = make_locations_markup(ways=WORLD[user_location]['ways'])
    description = WORLD[user_location]['description']
    bot.send_message(
        chat_id=user_id,
        text=f'<i>{description}</i>',
        reply_markup=markup,
        parse_mode='HTML'
    )


def make_locations_markup(ways):
    markup = ReplyKeyboardMarkup()
    for bottom in ways:
        markup.add(bottom)
    return markup


@bot.message_handler(func=lambda message: message.text == "1606")
def sixteen_six(message: Message):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton('Давай узнаем!', url='https://youtu.be/dQw4w9WgXcQ?si=MxA6xXlucyrelY9y')
    markup.add(button)
    bot.send_message(message.from_user.id, 'Интересно, что это значит?)', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['Поражение', "Победа"])
def win_wasted(message: Message):
    if message.text == "Победа":
        bot.send_message(message.from_user.id, "Поздравляю, вы победили! 🎉🎊")
    elif message.text == "Поражение":
        bot.send_message(message.from_user.id,
                         "К сожалению вы проиграли. Но ничего страшного, вы можете попытаться пройти игру еще раз!")
    bot.send_message(message.from_user.id, "Для того, чтобы начать заного, напишите /restart")


@bot.message_handler(func=lambda message: message.text == "Начать заново")
def restart(message: Message):
    user_id = str(message.from_user.id)
    register_new_user(message)
    savefile(users_data)
    send_user_location_bottoms(user_id)


@bot.message_handler(commands=["your_location"])
def send_user_location(message: Message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        location = users_data[user_id]['location_in_world']
        bot.send_message(user_id, f"Вы {WORLD[location]["guide"]}.")
    else:
        start_programm(message)


@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        return start_programm(message)
    user_location = users_data[user_id]['location_in_world']
    user_items = users_data[user_id]['user_items']

    if message.text in WORLD[user_location]['ways']:

        if message.text == "Запертая дверь" and "Старинный ключ" not in user_items:
            bot.send_message(user_id, "<b>Дверь на замке. Вам надо найти ключик</b>", parse_mode='HTML')
            return
        elif message.text == 'Запертая дверь' and "Старинный ключ" in user_items:
            users_data[user_id]['location_in_world'] = 'Запертая дверь'
            bot.send_message(user_id, "Ключ подошёл!")
            time.sleep(2)

        users_data[user_id]['location_in_world'] = message.text

        if message.text == "Барная стойка" and 'Старинный ключ' not in user_items:
            bot.send_message(user_id, "Вы подобрали старинный ключ!!!")
            users_data[user_id]['user_items'].append("Старинный ключ")
            time.sleep(1)
        send_user_location_bottoms(user_id)
    else:
        bot.send_message(
            user_id, "Пожалуйста, выберите один из предложенных вариантов в клавиатуре:"
        )
        savefile(users_data)


savefile(users_data)

bot.polling(none_stop=True)
