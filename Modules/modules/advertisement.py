import random
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.premiumdb import is_user_premium
from database.prdb import English, Russian, Azerbejani
from helpers.helper import get_users_list
from helpers.helper import find_language
from ..modules.impression import get_messages_list, get_message_details
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
                return
            await cbot.send_message(user_id, text=text, reply_markup=reply_markup)
    except AttributeError as e:
        print("An error occurred:", e)
        return

async def send_message(user_id: int, msg_id: int, msg_text: str, reply_markup, photo_link: str = None) -> None:
    """
    Send a message to a user with optional photo and reply markup.
    """
    if not user_id or not msg_id or not msg_text:
        raise ValueError("User ID, message ID, and message text are required")
    if reply_markup and not isinstance(reply_markup, InlineKeyboardMarkup):
        raise ValueError("Invalid reply markup")
    if photo_link and not isinstance(photo_link, str):
        raise ValueError("Invalid photo link")

    try:
        if photo_link:
            await cbot.send_photo(user_id, photo_link, msg_text, reply_markup=reply_markup)
        else:
            await cbot.send_message(user_id, msg_text, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error sending message to user {user_id} with message ID {msg_id}: {e}")


