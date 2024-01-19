import os
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from os import getenv
from dotenv import load_dotenv
from DATA_changes import *

load_dotenv()
token = getenv("bot_token")
bot = telebot.TeleBot(token)

world = load_world()
users_data = load_users_data()


@bot.message_handler(commands=['start'])
def start(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        register_new_user(message)
        hi(message)
    else:
        bot.send_message(user_id, "Если вы хотите перезагрузить игру, используйте команду /restart.")


def register_new_user(message):
    user_id = str(message.from_user.id)
    users_data[user_id] = {
        "username": message.from_user.username,
        "location_in_world": "start_place",
        "user_items": [],
        "user_achievements": []
    }
    savefile(users_data)


def hi(message):
    if message.from_user.id:
        user_name = message.from_user.id
    else:
        user_name = "пользователь"
    text = (
        f'Привет, {user_name}! Этот квест разрабатывался @Leoprofi. В случае ошибок, бездействия '
        'бота или прочих неудобств - обращайся к нему. \n'

        'Для полного погружения советую надеть наушники, а если ты не на телефоне, то в добавок открой чат с ботом '
        'на отдельное окно.\n'

        'Начинаем?')

    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton("Начать❕"))
    bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.message_handler(commands=['restart'])
def restart_game(message):
    user_id = str(message.from_user.id)
    users_data[user_id]["location_in_world"] = "start_place"
    users_data[user_id]["user_items"] = []
    bot.send_message(user_id, "Игра начинается заного...")


@bot.message_handler(func=lambda message: True)
def handler_answer(message: Message):
    user_id = str(message.from_user.id)
    make_locations_markup(user_id)


''' Клавиатура ⬇️ '''


def make_locations_markup(user_id):
    markup = ReplyKeyboardMarkup()
    user_location = users_data[user_id]['location_in_world']
    for bottom in world[user_location]['ways']:
        markup.add(bottom)
    return markup


bot.polling()
