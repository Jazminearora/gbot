import pyrogram
from pyrogram import filters, types
import random

from database.premiumdb import is_user_premium
from database.prdb import English, Russian, Azerbejani
from helpers.helper import find_language
from helpers.forcesub import user_registered, subscribed
from .. import cbot

async def advert_user(user_id):
    try:
        prem_user, ik = is_user_premium(user_id)
        print(prem_user, ik)
        if not prem_user:            
            lang = find_language(user_id)            
            if lang == "English":
                choices = list(English.values())  # Get a list of dictionary values
                choice = random.choice(choices)
                if choice:                    
                    if choice.get('photo_link'):
                        await cbot.send_photo(user_id, choice['photo_link'], caption=choice.get('text'), reply_markup=choice.get('reply_markup'))
                        return
                    else:
                        await cbot.send_message(user_id, text=choice.get('text'), reply_markup=choice.get('reply_markup'))
                        return
            elif lang == "Russian":
                choices = list(Russian.values())  # Get a list of dictionary values
                if not choices:
                    return
                choice = random.choice(choices)
                if not choice:
                    return
                if choice:                    
                    if choice.get('photo_link'):
                        await cbot.send_photo(user_id, choice['photo_link'], caption=choice.get('text'), reply_markup=choice.get('reply_markup'))
                        return
                    else:
                        await cbot.send_message(user_id, text=choice.get('text'), reply_markup=choice.get('reply_markup'))
                        return
            elif lang == "Azerbejani":
                choices = list(Azerbejani.values())  # Get a list of dictionary values
                if not choices:
                    return
                choice = random.choice(choices)
                if not choice:
                    return
                if choice:                    
                    if choice.get('photo_link'):
                        await cbot.send_photo(user_id, choice['photo_link'], caption=choice.get('text'), reply_markup=choice.get('reply_markup'))
                        return
                    else:
                        await cbot.send_message(user_id, text=choice.get('text'), reply_markup=choice.get('reply_markup'))
                        return
    except Exception as e:
        print("An error occurred:", e)
        return
