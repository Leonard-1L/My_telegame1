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


@bot.message_handler(commands=['start'])
def start_bot(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        register_new_user(message)
        hi(message)
    else:
        bot.send_message(user_id, "Здравствуй! Если ты хочешь перезагрузить игру, используйте команду /restart.")


def register_new_user(message):
    user_id = str(message.from_user.id)
    users_data[user_id] = {
        "username": message.from_user.username,
        "location_in_world": "start_place",
        "user_items": [],
        "user_achievements": [],
        "user_spaming": 0
    }
    savefile(users_data)


def hi(message):
    if message.from_user.id:
        user_name = message.from_user.username
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
def restart_user_game(message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        users_data[user_id]["location_in_world"] = "start_place"
        users_data[user_id]["user_items"] = []
        bot.send_message(user_id, "Игра начинается заного...")
        start_game(message)
    else:
        start_bot(message)


@bot.message_handler(func=lambda message: True)
def start_game(message: Message):
    user_id = str(message.from_user.id)
    for x in range(10):
        bot.send_message(message.from_user.id, "⬇️")
        time.sleep(0.1)
    if users_data[user_id]["user_spaming"] <= 2:
        with open("Media/Фоновая муза.mp3", "rb") as file:
            bot.send_audio(user_id, audio=file)
    else:
        bot.send_message(user_id, "Извини, но ты слишком часто перезапускал игру, я не могу присылать фоновую музыку.")
    users_data[user_id]["user_spaming"] += 1


# сделать вывод пути для пользователя, сделать сохранение предмета у пользователя при заход на новую локацию,
# вывод инвентаря пользователя, сделать больше локаций, сделать распознование куда идет пользователь


bot.polling()
