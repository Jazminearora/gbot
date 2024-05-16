from pyrogram import filters
from pyrogram.types import Message
from .. import cbot, ADMIN_IDS, LOG_GROUP
from helpers.shear import add_shear_word, get_all_shear_words, is_shear
from helpers.translator import translate_async
    
@cbot.on_message(filters.command("add_shear") & filters.user(ADMIN_IDS))
async def add_shear_word_handler(_, message: Message):
    """Add a shear word to the file"""
    if len(message.command) < 2:
        await message.reply_text("Usage: /add_shear <word>")
        return
    word = message.text.split(None, 1)[1]
    await add_shear_word(word)
    await message.reply_text(f"Added {word} to the list of shear words")

@cbot.on_message(filters.command("get_shear") & filters.user(ADMIN_IDS))
async def get_shear_words_handler(_, message: Message):
    """Get all shear words"""
    shear_words = await get_all_shear_words()
    await message.reply_text(f"Current shear words:\n\n {shear_words}")


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##


async def check_shear_url(user_id, message, lang):
    """
    Check if the message contains shear words or URLs and take appropriate action.
    """
    if await is_shear(message.text):
        await cbot.send_message(user_id, await translate_async("⚠️ Warning: Inappropriate language or insults are not tolerated here. Let's maintain a respectful conversation. Thank you! 🚫", lang))
        await cbot.forward_messages(LOG_GROUP, message.chat.id, message.id)
        await cbot.send_message(LOG_GROUP, f"""
    🚨 **Reported Message** 🚨

    **User ID:** {user_id}

    **Admin Note:**
    This message has been reported for containing inappropriate language or insults. Please review and take appropriate action. Thank you! 🛑
    """)
        return True

    if any(entity.type == "url" for entity in message.entities):
        await cbot.send_message(user_id, await translate_async("⚠️ Warning: URLs are not allowed in this chat. Please refrain from sharing links. Thank you! 🚫", lang))
        await cbot.forward_messages(LOG_GROUP, message.chat.id, message.id)
        await cbot.send_message(LOG_GROUP, f"""
    🚨 **Reported Message** 🚨

    **User ID:** {user_id}

    **Admin Note:**
    This message has been reported for containing a URL. Please review and take appropriate action. Thank you! 🛑
    """)
        return True

    return False