import time
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from os import getenv
from dotenv import load_dotenv
from DATA_changes import *
from actions_for_users import make_locations_markup, user_inventory, user_location_description, if_it_way, user_go

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
        time.sleep(6)
    else:
        bot.send_message(user_id, "Здравствуй! Если ты хочешь перезагрузить игру, используйте команду /restart.")


def register_new_user(message):
    user_id = str(message.from_user.id)
    users_data[user_id] = {
        "username": message.from_user.username,
        "location_in_world": "Начальная локация",
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

        'Для полного погружения советую надеть наушники, а если ты на пк/ноуте, то в добавок открой чат с ботом '
        'в отдельном окне.\n'

        'Начинаем?')

    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton("Начать❕"))
    bot.send_message(message.from_user.id, text, reply_markup=markup)
    time.sleep(4)


@bot.message_handler(commands=['restart'])
def restart_user_game(message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        users_data[user_id]["location_in_world"] = "Начальная локация"
        users_data[user_id]["user_items"] = []
        bot.send_message(user_id, "Cекунду...")
        savefile(users_data)
        time.sleep(1.5)
        markup = ReplyKeyboardMarkup()
        markup.add(KeyboardButton("Начать❕"))
        bot.send_message(message.from_user.id, "Готово, начинаем?", reply_markup=markup)
        bot.register_next_step_handler(message, start_game)
    else:
        start_bot(message)


@bot.message_handler(commands=["your_items"])
def send_user_items(message: Message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        inventary = user_inventory(user_id)
        if inventary != "":
            bot.send_message(user_id, inventary)
        else:
            bot.send_message(user_id, "У вас в инвентаре ничего нет.")
    else:
        start_bot(message)


@bot.message_handler(commands=["your_location"])
def send_user_location(message: Message):
    user_id = str(message.from_user.id)
    if user_id in users_data:
        location = users_data[user_id]['location_in_world']
        bot.send_message(user_id, f"Ты находишся {WORLD[location]["guide"]}.")
    else:
        start_bot(message)


'''Обработка мира ⬇️'''


@bot.message_handler(func=lambda message: if_it_way(message))
def user_path_processing(message: Message):
    try:
        user_id = str(message.from_user.id)
        if message.text == 'Запертая дверь':
            if "Золотой ключик" in users_data[user_id]["user_items"]:
                bot.send_message(user_id, "Отлично! Ключ подошёл!")
                user_go(message)
            else:
                location_markup = make_locations_markup(user_id)
                bot.send_message(user_id, "О нет! Дверь заперта. Нужно найти где-то ключ.\n"
                                          "<b>Выбери путь:</b>", reply_markup=location_markup, parse_mode='HTML')
        if message.text == "Обменять все свои вещи в инвентаре на мантию-невидимку":
            if "Золотая монетка" in users_data[user_id]["user_items"]:
                bot.send_message(user_id,
                                 "Обмен прошел успешно. Незнакомец продал вам мантию-неведимку.",
                                 reply_markup=make_locations_markup(user_id))
                users_data[user_id]["user_items"] = ["Мантия-невидимка"]
                return
            else:
                bot.send_message(user_id, "Незнакомец глядя на ваш инвентарь отказался от сделки.",
                                 reply_markup=make_locations_markup(user_id)
                                 )
                return
        user_go(message)
        location_description = user_location_description(message)
        location_markup = make_locations_markup(user_id)
        bot.send_message(user_id, text=f"<i>{location_description}</i>\n"
                                       "\n"
                                       "<b>Выбери путь:</b>", reply_markup=location_markup, parse_mode='HTML')
    except Exception as E:
        print(f'{E} by {message.from_user.username} in path_processihg')
        bot.send_message(message.from_user.id, "У нас на сервере техническая школадочка, приносим извинения!")
        bot.register_next_step_handler(message, start_game)


@bot.message_handler(func=lambda message: True)
def start_game(message: Message):
    try:
        user_id = str(message.from_user.id)
        if user_id not in users_data:
            bot.register_next_step_handler(message, start_bot)
        if message.text == "Начать❕":
            game_atmosphera(message)
            location_markup = make_locations_markup(user_id)
            text = WORLD['Начальная локация']['description']
            bot.send_message(user_id, f"<i>{text}</i>", parse_mode='HTML')
            time.sleep(4)
            bot.send_message(user_id, "<i>Ничего не оствается, тебе придется пойти..</i>", reply_markup=location_markup,
                             parse_mode='HTML')
        else:
            bot.send_message(user_id, "Не могу распознать сообщение. Выбери действие в предложенной клавиатуре.")
    except Exception as E:
        print(f'{E} by {message.from_user.username} in start game')
        bot.send_message(message.from_user.id, "У нас на сервере техническая неполадочка, приносим извинения!")
        bot.register_next_step_handler(message, start_game)


def game_atmosphera(message: Message):
    user_id = str(message.from_user.id)
    if users_data[user_id]["user_restart_spaming"] <= 3:
        with open("Media/Фоновая муза.mp3", "rb") as file:
            bot.send_audio(user_id, audio=file)
    else:
        msg = bot.send_message(user_id,
                               "Ты слишком часто перезапускал игру, я больше не могу присылать фоновую музыку.")
        time.sleep(2)
        bot.delete_message(user_id, msg.id)

    bot.send_message(user_id, "Совет: Используйте наушники для глобального погружения")
    bot.send_message(user_id, "Игра начинается...")
    time.sleep(3)
    for x in range(10):
        bot.send_message(message.from_user.id, "⬇️")  # путем спама скрывает предыдущие игры
        time.sleep(0.1)
    users_data[user_id]["user_restart_spaming"] += 1
    savefile(users_data)


#  сделать сохранение предмета у пользователя при заход на новую локацию,
# сделать больше локаций
savefile(users_data)

bot.polling()
