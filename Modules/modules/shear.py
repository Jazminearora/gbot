import os
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import MessageEntityType
import pyrostep
from .. import cbot, ADMIN_IDS, LOG_GROUP, BOT_USERNAME
from helpers.shear import add_shear_word, get_all_shear_words, is_shear
from helpers.translator import translate_async
    
pyrostep.listen(cbot)

markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Add Shear ➕", callback_data="plus_shear_word"),
         InlineKeyboardButton(text= "Shear Action ⚙️", callback_data= "shear_action")],
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]])

@cbot.on_callback_query(filters.regex("shear_control") & filters.user(ADMIN_IDS))
async def get_shear_words_handler(_, callback_query: CallbackQuery):
    """Get all shear words"""
    shear_words1 = await get_all_shear_words("en")
    shear_words2 = await get_all_shear_words("az")
    shear_words3 = await get_all_shear_words("ru")
    await callback_query.message.edit_text(f"Current shear words:\n\n**English**\n{shear_words1}\n\n**Azerbejani**\n{shear_words2}\n\n**Russian**\n{shear_words3}", reply_markup=markup)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

@cbot.on_callback_query(filters.regex("plus_shear_word") & filters.user(ADMIN_IDS))
async def add_shear_word_handler(_, callback_query: CallbackQuery):
    """Ask user to input new shear words"""
    lang_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Azerbaijani (az)", callback_data="lang_shear_az"),
         InlineKeyboardButton(text="Russian (ru)", callback_data="lang_shear_ru"),
         InlineKeyboardButton(text="English (en)", callback_data="lang_shear_en")]
    ])
    await callback_query.message.edit_text("Choose the language for the new shear words:", reply_markup=lang_markup)

@cbot.on_callback_query(filters.regex(r"lang_shear_(az|ru|en)") & filters.user(ADMIN_IDS))
async def choose_lang_handler(_, callback_query: CallbackQuery):
    """Ask user to input new shear words"""
    lang = callback_query.data.split("_")[2]
    await callback_query.message.edit_text("Enter new shear words, separated by new lines:")
    user_id = callback_query.from_user.id
    shear_words_message = await pyrostep.wait_for(user_id)
    shear_words = shear_words_message.text
    new_shear_words = [word.strip() for word in shear_words.splitlines()]
    for word in new_shear_words:
        await add_shear_word(word, lang)
    await callback_query.answer(f"Added all words to the list of shear words in {lang}", show_alert=True)
    shear_words1 = await get_all_shear_words("en")
    shear_words2 = await get_all_shear_words("az")
    shear_words3 = await get_all_shear_words("ru")
    await callback_query.message.edit_text(f"Current shear words:\n\n**English**\n{shear_words1}\n\n**Azerbejani**\n{shear_words2}\n\n**Russian**\n{shear_words3}", reply_markup=markup)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##


@cbot.on_callback_query(filters.regex("shear_action") & filters.user(ADMIN_IDS))
async def shear_action_handler(_, callback_query: CallbackQuery):
    """Shear action callback"""
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ban ⚫️", callback_data="shear_ban"), InlineKeyboardButton("Warn ⚠️", callback_data="shear_warn")],
        [InlineKeyboardButton("Time Ban ⏰", callback_data="shear_time-ban"), InlineKeyboardButton("OFF 📴", callback_data="shear_off")],
        [InlineKeyboardButton("Close ❌", callback_data="st_close"), InlineKeyboardButton("Back 🔙", callback_data="st_back")]
    ])
    current = os.getenv("SHEAR_ACTION") if os.getenv("SHEAR_ACTION")  else "ban"
    await callback_query.message.edit_text(f"Curent status: {current} \n\nChoose an action for shear words:", reply_markup=markup)

@cbot.on_callback_query(filters.regex(r"shear_(ban|warn|time-ban|off)") & filters.user(ADMIN_IDS))
async def set_shear_action_handler(_, callback_query: CallbackQuery):
    """Set SHEAR_ACTION"""
    action = callback_query.data.split("_")[1]
    os.environ["SHEAR_ACTION"] = action
    await callback_query.answer(f"Shear action set to {action}", show_alert=True)
    shear_words1 = await get_all_shear_words("en")
    shear_words2 = await get_all_shear_words("az")
    shear_words3 = await get_all_shear_words("ru")
    await callback_query.message.edit_text(f"Current shear words:\n\n**English**\n{shear_words1}\n\n**Azerbejani**\n{shear_words2}\n\n**Russian**\n{shear_words3}", reply_markup=markup)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##


async def check_shear_url(user_id, message, lang):
    """
    Check if the message contains shear words or URLs and take appropriate action.
    """
    current = os.getenv("SHEAR_ACTION") if os.getenv("SHEAR_ACTION")  else "ban"
    if current == "off":
        return False
    if await is_shear(message.text, lang) if message.text else await is_shear(message.caption, lang):
        await cbot.send_message(user_id, await translate_async("⚠️ Warning: Inappropriate language or insults are not tolerated here. Let's maintain a respectful conversation. Thank you! 🚫", lang))
        sz = await cbot.forward_messages(LOG_GROUP, message.chat.id, message.id)
        user_link = f"<a href='https://t.me/{BOT_USERNAME}?start=id{user_id}'>{user_id}</a>"
        await cbot.send_message(LOG_GROUP, f"""
    🚨 **Reported Message** 🚨

    **User ID:** {user_link}

    **Admin Note:**
    This message has been reported for containing inappropriate language or insults. Please review and take appropriate action. Thank you! 🛑
    """, reply_to_message_id= sz.id)
        return True

    elif message.entities and any(entity.type == MessageEntityType.URL for entity in message.entities):
        await cbot.send_message(user_id, await translate_async("⚠️ Warning: URLs are not allowed in this chat. Please refrain from sharing links. Thank you! 🚫", lang))
        sk = await cbot.forward_messages(LOG_GROUP, message.chat.id, message.id)
        await cbot.send_message(LOG_GROUP, f"""
    🚨 **Reported Message** 🚨

    **User ID:** {user_id}

    **Admin Note:**
    This message has been reported for containing a URL. Please review and take appropriate action. Thank you! 🛑
    """, reply_to_message_id= sk.id)
        return True

    return False