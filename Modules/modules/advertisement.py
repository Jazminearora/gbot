import random
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.premiumdb import is_user_premium
from database.prdb import English, Russian, Azerbejani
from helpers.helper import get_users_list
from helpers.helper import find_language
from Modules.modules.impression import get_messages_list, get_message_details
from .. import cbot


prem_user_cache = {}

async def advert_user(user_id, lang, prem: bool = None):
    try:
        if prem is None:
            prem_user = prem_user_cache.get(user_id)
            if prem_user is None:
                prem_user, _ = is_user_premium(user_id)
                prem_user_cache[user_id] = prem_user
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
            message_id = random.choice(list(messages.keys()))
            message = messages[message_id]
            if not message:
                return
            text = message.get('text')
            button_details = message.get('button_details', [])
            reply_markup = None
            if button_details:
                keyboard = [InlineKeyboardButton(btn['btn_text'], url=btn['btn_url']) for btn in button_details]
                reply_markup = InlineKeyboardMarkup([keyboard])
            if message.get("photo_link"):
                photo = message.get("photo_link")
                await cbot.send_photo(user_id, photo, text, reply_markup= reply_markup)
            await cbot.send_message(user_id, text=text, reply_markup=reply_markup)
    except AttributeError as e:
        print("An error occurred:", e)
        return

async def send_message(user_id: int, msg_text: str, reply_markup, photo_link: str = None) -> None:
    if photo_link:
        await cbot.send_photo(user_id, photo_link, msg_text, reply_markup=reply_markup)
    else:
        await cbot.send_message(user_id, msg_text, reply_markup=reply_markup)

async def sheduled_promo_code() -> None:
    while True:
        messages_list = await get_messages_list()
        if not messages_list:
            await asyncio.sleep(60)  # sleep for 1 minute if no messages
            continue

        for msg_id, duration, language in messages_list:
            msg_details = await get_message_details(msg_id)
            if not msg_details:
                continue

            msg_text = msg_details.get("text")
            inline_btn = msg_details.get("button_details")
            reply_markup = None
            if inline_btn:
                keyboard = [InlineKeyboardButton(btn['btn_text'], url=btn['btn_url']) for btn in inline_btn]
                reply_markup = InlineKeyboardMarkup([keyboard])

            photo_link = msg_details.get("photo_link")
            lang = language

            while True:
                users = await get_users_list(lang)
                for user in users:
                    try:
                        await send_message(user, msg_text, reply_markup, photo_link)
                    except Exception as e:
                        print(f"Error sending message to user {user}: {e}")

                await asyncio.sleep(duration * 60 * 60)  # sleep for the specified duration

                new_messages_list = await get_messages_list()
                if msg_id not in [msg[0] for msg in new_messages_list]:
                    break  # break the loop if the message is no longer in the list