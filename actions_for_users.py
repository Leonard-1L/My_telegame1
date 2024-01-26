from DATA_changes import *
from telebot.types import ReplyKeyboardMarkup

WORLD = load_world()
users_data = load_users_data()

''' Клавиатура ⬇️ '''





''' Инвентарь ⬇️ '''


def user_inventory(user_id):
    inventory = ""
    for item in users_data[user_id]["user_items"].value():
        inventory += "- " + item + "\n"
    return inventory


def user_put_up(user_id):
    user_location = users_data[user_id]['location_in_world']
    items = WORLD[user_location]['location_items']
    for x in items:
        if x not in users_data[user_id]['user_items']:
            users_data[user_id]['user_items'][x] = "Было в инвентаре"


''' Обработка путей для пользователя'''


def if_it_way(message):
    user_location = users_data[str(message.from_user.id)]['location_in_world']
    return message.text in WORLD[user_location]['ways']


def user_location_description(user_id):
    return WORLD[users_data[user_id]['location_in_world']]['description']


def user_go(user_id):
    users_data[user_id]['location_in_world'] = user_id
    savefile(users_data)
