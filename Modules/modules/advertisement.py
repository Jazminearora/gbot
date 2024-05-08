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
                choice = random.choice(English)
                if choice:
                    print("Selected choice:", choice)
                    
                    if choice.photo_link:
                        print("Sending photo to user:", user_id)
                        await cbot.send_photo(user_id, choice.photo_link, caption=choice.text if choice.text else None, reply_markup=choice.reply_markup if choice.reply_markup else None)
                        print("Photo sent successfully")
                        return
                    else:
                        print("Sending text message to user:", user_id)
                        await cbot.send_message(user_id, text=choice.text, reply_markup=choice.reply_markup if choice.reply_markup else None)
                        print("Text message sent successfully")
                        return
    except Exception as e:
        print("An error occurred:", e)
        return
