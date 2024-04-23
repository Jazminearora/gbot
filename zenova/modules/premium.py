from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup
import re


from zenova import zenova 
from helpers.helper import find_language
from helpers.get_msg import get_premium_msg



button_pattern = re.compile(r"^💎 (Premium|Премиум|Premium) 💎$")
@zenova.on_message(filters.private & filters.regex(button_pattern))
async def premium_option(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    message_text, inline_buttons = await get_premium_msg(language)
    inline_keyboard = [buttons for buttons in inline_buttons]
    await message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(inline_keyboard))