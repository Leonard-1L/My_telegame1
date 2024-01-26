import time
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from os import getenv
from dotenv import load_dotenv
from DATA_changes import *

load_dotenv()
TOKEN = getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

WORLD = load_world()
users_data = load_users_data()


@bot.message_handler(commands=['start', 'restart'])
def start_programm(message: Message):
    markup = ReplyKeyboardMarkup()
    user_id = str(message.from_user.id)

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
    elif user_id in users_data and users_data[user_id]['location_in_world'] != "Начальная локация":
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
    markup = make_locations_markup(ways=WORLD[user_location]['ways'])
    description = WORLD[user_location]['description']
    bot.send_message(
        chat_id=user_id,
        text=f'<i>{description}</i>',
        reply_markup=markup,
        parse_mode='HTML'
    )
    # bot.send_photo(
    #     chat_id=user_id,
    #     photo=open(f"Media/{image}", "rb")
    # )


def make_locations_markup(ways):
    markup = ReplyKeyboardMarkup()
    for bottom in ways:
        markup.add(bottom)
    return markup


# @bot.message_handler(func=lambda message: message.text in ['Поражение', "Победа"])
@bot.message_handler(func=lambda message: message.text == "Начать заново")
def restart(message: Message):
    user_id = str(message.from_user.id)
    users_data[user_id] = {
        "location_in_world": "Начальная локация",
        "user_items": []
    }
    savefile(users_data)
    send_user_location_bottoms(user_id)


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

        users_data[user_id]['location_in_world'] = message.text

        if message.text == "Барная стойка" and 'Старинный ключ' not in user_items:
            bot.send_message(user_id, "Вы подобрали старинный ключ!!!")
            users_data[user_id]['user_items'].append("Старинный ключ")
        send_user_location_bottoms(user_id)
    else:
        bot.send_message(
            user_id, "Пожалуйста, выберите один из предложенных вариантов в клавиатуре:"
        )
        savefile(users_data)


bot.polling(none_stop=True)
