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


@bot.message_handler(commands=['start'])
def start_bot(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        register_new_user(message)
        hi(message)
    else:
        users_data[user_id]["location_in_world"] = "Начальная локация"
        users_data[user_id]["user_items"] = {}
        markup = ReplyKeyboardMarkup()
        markup.add(KeyboardButton("Начать❕"))
        bot.send_message(user_id,
                         f"Здравствуй вновь, {message.from_user.username}! Если ты хочешь перезагрузить игру, "
                         f"напиши начать.", reply_markup=markup)


def register_new_user(message):
    user_id = str(message.from_user.id)
    users_data[user_id] = {
        "username": message.from_user.username,
        "location_in_world": "Начальная локация",
        "user_items": {},
        "user_achievements": [],
        "user_restart_spaming": 0
    }
    savefile(users_data)


def hi(message):
    if message.from_user.username is None:
        user_name = "пользователь"
    else:
        user_name = message.from_user.username

    text = (
        f'Привет, {user_name}! Этот квест разрабатывался @Leoprofi. В случае ошибок, бездействия '
        'бота или прочих неудобств - обращайся к нему. \n'

        'Для полного погружения советую надеть наушники, а если ты на пк/ноуте, то в добавок открой чат с ботом '
        'в отдельном окне.\n'

        'Начинаем?')
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton("Начать❕"))
    bot.send_message(message.from_user.id, text, reply_markup=markup)
    time.sleep(1)


@bot.message_handler(func=lambda message: message.text == "Начать❕")
def start_first_location(message: Message):
    user_id = str(message.from_user.id)
    game_atmosphera(message)
    markup = ReplyKeyboardMarkup()
    markup.add(KeyboardButton("Первый этаж"))
    text = "Вас окружает просторное поле. Недалеко виднеется единственный обьект - какое-то трехэтажное и заброшенное здание. Идти больше некуда."
    bot.send_message(user_id, f"<i>{text}</i>", parse_mode='HTML')
    time.sleep(1)
    bot.send_message(user_id, "<i>Зайти в здание на первый этаж?</i>", reply_markup=markup,
                     parse_mode='HTML')


def if_it_wy(message):
    user_location = users_data[str(message.from_user.id)]['location_in_world']
    if message.text in WORLD[user_location]['ways']:
        return True
    else:
        return False


@bot.message_handler(func=lambda message: True)
def start_game(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        start_bot(message)
    if if_it_wy(message):
        user_path_processing(message)
    else:
        bot.send_message(user_id, "Я не понял ваше сообщение. Используйте предложенные кнопки на экране")
    savefile(users_data)


def game_atmosphera(message: Message):
    user_id = str(message.from_user.id)
    if users_data[user_id]["user_restart_spaming"] <= 3:
        with open("Media/Фоновая муза.mp3", "rb") as file:
            bot.send_audio(user_id, audio=file)
    else:
        msg = bot.send_message(user_id,
                               "Ты слишком часто перезапускал игру, я больше не могу присылать фоновую музыку.")
        bot.delete_message(user_id, msg.id)
        time.sleep(1)
    bot.send_message(user_id, "Совет: Используйте наушники для глобального погружения")
    bot.send_message(user_id, "Игра начинается...")
    time.sleep(3)
    for x in range(10):
        bot.send_message(message.from_user.id, "⬇️")  # путем спама скрывает предыдущие игры
        time.sleep(0.2)
    users_data[user_id]["user_restart_spaming"] += 1
    savefile(users_data)


def user_path_processing(message: Message):
    user_id = str(message.from_user.id)
    if message.text == 'Запертая дверь':
        if "Золотой ключик" in users_data[user_id]["user_items"]:
            users_data[user_id]['location_in_world'] = 'Запертая дверь'
            bot.send_message(user_id,
                             "Отлично! Ключ подошёл! Куда пойдешь?",
                             reply_markup=make_locations_markup(user_id))

        else:
            location_markup = ReplyKeyboardMarkup()
            location_markup.add(KeyboardButton("Подвал"))
            bot.send_message(user_id, "О нет! Дверь заперта. Нужно найти где-то ключ.\n"
                                      "<b>Возвращайся назад</b>", reply_markup=location_markup, parse_mode='HTML')

    elif message.text == "Обменять все свои вещи в инвентаре на мантию-невидимку":
        if "Золотая монетка" in users_data[user_id]["user_items"]:
            location_markup = ReplyKeyboardMarkup()
            location_markup.add(KeyboardButton("Запертая дверь"))
            bot.send_message(user_id,
                             "Обмен прошел успешно. Незнакомец продал вам мантию-невидимку. Возвращайтесь назад.",
                             reply_markup=location_markup)
            users_data[user_id]["user_items"] = {"Мантия-невидимка"}
        else:
            location_markup = ReplyKeyboardMarkup()
            location_markup.add(KeyboardButton("Запертая дверь"))
            bot.send_message(user_id,
                             "Незнакомец глядя на ваш инвентарь отказался от сделки. Возвращайтесь назад "
                             "и ищите что-то ценное",
                             reply_markup=location_markup
                             )
    else:
        users_data[user_id]['location_in_world'] = message.text
        location_markup = make_locations_markup(user_id)
        location_description = user_location_description(user_id)
        bot.send_message(user_id, text=f"<i>{location_description}</i>\n"
                                       "\n"
                                       "<b>Выбери путь:</b>", reply_markup=location_markup, parse_mode='HTML')
    savefile(users_data)


savefile(users_data)

bot.polling()
