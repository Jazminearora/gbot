import random
import asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import filters
from database.premiumdb import is_user_premium
from database.prdb import English, Russian, Azerbejani
from .. import cbot

AUTO_PROMO = True

prem_user_cache = {}

@cbot.on_callback_query(filters.regex(r'^toggle_auto$'))
async def toggle_auto_handler(_, query):
    global AUTO_PROMO
    AUTO_PROMO = not AUTO_PROMO
    text = f"Auto Promo Status: {'ON' if AUTO_PROMO else 'OFF'} 🔄\n\n\
Auto Promo automatically promotes your content. Turn it {'OFF' if AUTO_PROMO else 'ON'} if you prefer manual control."
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Toggle {'❌ OFF' if AUTO_PROMO else '✅ ON'}", callback_data="toggle_auto")],
        [InlineKeyboardButton(f"Back 🔙", callback_data="st_back"),
         InlineKeyboardButton(f"Close ❌", callback_data="st_close")]
    ])
    await query.message.edit_text(text, reply_markup=markup)

@cbot.on_callback_query(filters.regex(r'^st_auto$'))
async def auto_promo_handler(_, query):
    global AUTO_PROMO
    text = f"Auto Promo Status: {'ON' if AUTO_PROMO else 'OFF'} 🔄\n\n\
Auto Promo automatically promotes your content. Turn it {'OFF' if AUTO_PROMO else 'ON'} if you prefer manual control."
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Toggle {'❌ OFF' if AUTO_PROMO else '✅ ON'}", callback_data="toggle_auto")],
        [InlineKeyboardButton(f"Back 🔙", callback_data="st_back"),
         InlineKeyboardButton(f"Close ❌", callback_data="st_close")]
    ])
    await query.message.edit_text(text, reply_markup=markup)

async def advert_user(user_id, lang, prem: bool = None):
    global AUTO_PROMO
    if not AUTO_PROMO:
        return
    try:
        prem_user, _ = is_user_premium(user_id)
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
    prem_user, _ = is_user_premium(user_id)
    if prem_user:
        return
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


