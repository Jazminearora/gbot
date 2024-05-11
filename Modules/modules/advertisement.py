import random
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
            lang_dict = {
                "english": English,
                "russian": Russian,
                "azerbaijani": Azerbejani
            }
            lang = lang.lower()
            if lang not in lang_dict:
                return
            messages = lang_dict[lang]
            if not messages:
                return
            message_ids = list(messages.keys())
            if not message_ids:
                return
            message_id = random.choice(message_ids)
            if not message_id:
                return
            message = messages[message_id]
            if not message:
                return
            text = message.get('text')
            button_details = message.get('button_details', [])
            reply_markup = None
            if button_details:
                keyboard = [[InlineKeyboardButton(btn['btn_text'], url=btn['btn_url'])] for btn in button_details]
                reply_markup = InlineKeyboardMarkup(keyboard)
            await cbot.send_message(user_id, text=text, reply_markup=reply_markup)
    except AttributeError as e:
        print("An error occurred:", e)
        return
