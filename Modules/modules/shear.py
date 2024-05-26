from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import MessageEntityType
import pyrostep
from .. import cbot, ADMIN_IDS, LOG_GROUP
from helpers.shear import add_shear_word, get_all_shear_words, is_shear
from helpers.translator import translate_async
    
pyrostep.listen(cbot)

markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Add Shear Word ➕", callback_data="add_shear_word")],
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]])

@cbot.on_callback_query(filters.regex("shear_control") & filters.user(ADMIN_IDS))
async def get_shear_words_handler(_, callback_query: CallbackQuery):
    """Get all shear words"""
    shear_words = await get_all_shear_words()
    await callback_query.message.edit_text(f"Current shear words:\n\n{shear_words}", reply_markup=markup)

@cbot.on_callback_query(filters.regex("add_shear_word") & filters.user(ADMIN_IDS))
async def add_shear_word_handler(_, callback_query: CallbackQuery):
    """Ask user to input new shear words"""
    await callback_query.message.edit_text("Enter new shear words, separated by new lines:")
    user_id = callback_query.from_user.id
    shear_words_message = await pyrostep.wait_for(user_id)
    shear_words = shear_words_message.text
    new_shear_words = [word.strip() for word in shear_words.splitlines()]
    for word in new_shear_words:
        await add_shear_word(word)
    await callback_query.answer(f"Added all words to the list of shear words", show_alert= True)
    shear_words = await get_all_shear_words()
    await callback_query.message.edit_text(f"Current shear words:\n\n{shear_words}", reply_markup=markup)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##


async def check_shear_url(user_id, message, lang):
    """
    Check if the message contains shear words or URLs and take appropriate action.
    """
    if await is_shear(message.text) if message.text else await is_shear(message.caption):
        await cbot.send_message(user_id, await translate_async("⚠️ Warning: Inappropriate language or insults are not tolerated here. Let's maintain a respectful conversation. Thank you! 🚫", lang))
        sz = await cbot.forward_messages(LOG_GROUP, message.chat.id, message.id)
        await cbot.send_message(LOG_GROUP, f"""
    🚨 **Reported Message** 🚨

    **User ID:** {user_id}

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