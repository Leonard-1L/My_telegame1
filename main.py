import time
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from os import getenv
from dotenv import load_dotenv
from DATA_changes import *
from actions_for_users import make_locations_markup, user_inventory

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
        game_atmosphera(message)
    else:
        bot.send_message(user_id, "Здравствуй! Если ты хочешь перезагрузить игру, используйте команду /restart.")


def register_new_user(message):
    user_id = str(message.from_user.id)
    users_data[user_id] = {
        "username": message.from_user.username,
        "location_in_world": "start_place",
        "user_items": [],
        "user_achievements": [],
        "user_restart_spaming": 0
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
        game_atmosphera(message)
    else:
        start_bot(message)


@bot.message_handler(commands=["your_items"])
def send_user_items(message: Message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        inventary = user_inventory(user_id)
        if not inventary == "":
            bot.send_message(user_id, inventary)
        else:
            bot.send_message(user_id, "у вас в инвентаре ничего нет.")
    else:
        start_bot(message)


@bot.message_handler(commands=["your_location"])
def send_user_location(message: Message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        bot.send_message(user_id, f"Вы находитесь {users_data[user_id]['location_in_world']}")
    else:
        start_bot(message)


@bot.message_handler(func=lambda message: True)
def start_game(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        start_bot(message)
    if users_data[user_id]["location_in_world"] == "start_place":
        game_atmosphera(message)


def game_atmosphera(message: Message):
    user_id = str(message.from_user.id)
    for x in range(10):
        bot.send_message(message.from_user.id, "⬇️")
        time.sleep(0.1)
    if users_data[user_id]["user_restart_spaming"] <= 2:
        with open("Media/Фоновая муза.mp3", "rb") as file:
            bot.send_audio(user_id, audio=file)
    else:
        bot.send_message(user_id,
                         "Извини, но ты слишком часто перезапускал игру, я не могу присылать фоновую музыку.")
    users_data[user_id]["user_restart_spaming"] += 1


'''Обработка мира ⬇️'''

#  сделать сохранение предмета у пользователя при заход на новую локацию,
# сделать больше локаций, сделать распознование куда идет пользователь


bot.polling()
