from pyrogram import filters
import re


from zenova import zenova 
from helpers.helper import find_language
from helpers.get_msg import get_premium_msg



button_pattern = re.compile(r"^💎 (Premium|Премиум|Premium) 💎$")
@zenova.on_message(filters.private & filters.regex(button_pattern))
async def premium_option(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    message, buttons = await get_premium_msg(language)
    await message.reply_text(message, reply_markup=buttons)