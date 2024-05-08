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
        if not is_user_premium(user_id):
            if find_language(user_id) == "English":
                choice = random.choice(English)
                if choice:
                    if choice.photo_link:
                        await cbot.send_photo(user_id, choice.photo_link, caption = choice.text if choice.text else None, reply_markup= choice.reply_markup if choice.reply_markup else None)
                        return
                    else:
                        await cbot.send_message(user_id, text = choice.text, reply_markup= choice.reply_markup if choice.reply_markup else None)
                        return
    except Exception as e:
        print("An error occured:", e)
        return