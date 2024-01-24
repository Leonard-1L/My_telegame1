import DATA_changes
from telebot.types import ReplyKeyboardMarkup

WORLD = DATA_changes.load_world()
users_data = DATA_changes.load_users_data()

''' Клавиатура ⬇️ '''


def make_locations_markup(user_id):
    markup = ReplyKeyboardMarkup()
    user_location = users_data[str(user_id)]['location_in_world']
    for bottom in WORLD[user_location]['ways']:
        markup.add(bottom)
    return markup


''' Инвентарь ⬇️ '''


def user_inventory(user_id):
    inventory = ""
    for item in users_data[user_id]["user_items"]:
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
    if message.text in WORLD[user_location]['ways']:
        return True
    else:
        return False


def user_location_description(message):
    user_id = str(message.from_user.id)
    return WORLD[users_data[user_id]['location_in_world']]['description']


def user_go(message):
    user_id = str(message.from_user.id)
    users_data[user_id]['location_in_world'] = message.text
    DATA_changes.savefile(users_data)
