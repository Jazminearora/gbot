import random

from database.premiumdb import is_user_premium
from database.prdb import English, Russian, Azerbejani
from helpers.helper import find_language
from .. import cbot

async def advert_user(user_id, lang, prem: bool = None):
    try:
        if prem is None:
            prem_user, _ = is_user_premium(user_id)
        else:
            prem_user = prem
        if not prem_user:
            language_dicts = {
                "English": English,
                "Russian": Russian,
                "Azerbejani": Azerbejani
            }
            lang_dict = language_dicts.get(lang)
            if not lang_dict:
                return
            choices = list(lang_dict.values())
            if not choices:
                return
            choice = random.choice(choices)
            if not choice:
                return
            if choice.get('photo_link'):
                await cbot.send_photo(user_id, choice['photo_link'], caption=choice.get('text'), reply_markup=choice.get('reply_markup'))
            else:
                await cbot.send_message(user_id, text=choice.get('text'), reply_markup=choice.get('reply_markup'))
    except AttributeError as e:
        print("An error occurred:", e)
        return