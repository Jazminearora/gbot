import pyrogram
from pyrogram import filters, types
import random

from database.premiumdb import is_user_premium
from database.prdb import English, Russian, Azerbejani
from helpers.helper import find_language
from helpers.forcesub import user_registered, subscribed
from .. import cbot

async def advert_user(user_id):
    print("function called")
    try:
        prem_user, ik = is_user_premium(user_id)
        print(prem_user, ik)
        if not prem_user:
            print("User is not premium")
            
            lang = find_language(user_id)
            print("User language:", lang)
            
            if lang == "English":
                print(English)
                choices = list(English.values())  # Get a list of dictionary values
                choice = random.choice(choices)
                if choice:
                    print("Selected choice:", choice)
                    
                    if choice.get('photo_link'):
                        print("Sending photo to user:", user_id)
                        await cbot.send_photo(user_id, choice['photo_link'], caption=choice.get('text'), reply_markup=choice.get('reply_markup'))
                        print("Photo sent successfully")
                        return
                    else:
                        print("Sending text message to user:", user_id)
                        await cbot.send_message(user_id, text=choice.get('text'), reply_markup=choice.get('reply_markup'))
                        print("Text message sent successfully")
                        return
    except Exception as e:
        print("An error occurred:", e)
        return
