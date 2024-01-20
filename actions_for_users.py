import DATA_changes
from telebot.types import ReplyKeyboardMarkup

WORLD = DATA_changes.load_world()
users_data = DATA_changes.load_users_data()

''' Клавиатура ⬇️ '''


def make_locations_markup(user_id):
    markup = ReplyKeyboardMarkup()
    user_location = users_data[user_id]['location_in_world']
    for bottom in WORLD[user_location]['ways']:
        markup.add(bottom)
    return markup
