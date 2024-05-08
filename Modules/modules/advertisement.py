import pyrogram
from pyrogram import filters, types
import random

from database.premiumdb import is_user_premium
from database.prdb import English, Russian, Azerbejani
from helpers.helper import find_language
from helpers.forcesub import user_registered, subscribed
from .. import cbot

@cbot.on_message(filters.incoming, filters.private & subscribed & user_registered)
async def advert_user(_, message):
    user_id = message.from_user.id
    if not is_user_premium(user_id):
        if find_language(user_id) == "English":
            choice = random.choice(English)
            if choice:
                if choice.photo_link:
                    await message.reply_photo(choice.photo_link, caption = choice.text if choice.text else None, reply_markup= choice.reply_markup if choice.reply_markup else None)
                else:
                    await message.reply_text(caption = choice.text, reply_markup= choice.reply_markup if choice.reply_markup else None)