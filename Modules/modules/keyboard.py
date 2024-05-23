from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from Modules import cbot, BOT_USERNAME
import re


# Helper functions
from Modules.modules.advertisement import advert_user
from helpers.forcesub import subscribed, user_registered
from helpers.helper import find_language
from langdb.get_msg import get_reply_markup 
from helpers.translator import translate_async


SELECT_OPTION_PHOTO = "https://iili.io/JgY8Fls.jpg"


# Handle private messages with the reply markup
@cbot.on_message(filters.command(["start"]) & filters.private & subscribed & user_registered)
async def start_command(client, message):
    print("strt called")
    await home_page(message)

@cbot.on_message(filters.regex("Back|Назад|Geri") & filters.private & subscribed & user_registered) 
async def back_command(client, message):
    await home_page(message)


async def home_page(message):
    try:
        user_id = message.from_user.id
        language = find_language(user_id)
        await advert_user(user_id, language)
        reply_markup = await get_reply_markup(language)
        text = await translate_async("Please select an option:", language)
        await message.reply_photo(SELECT_OPTION_PHOTO, caption = text, reply_markup=reply_markup)
    except Exception as e:
        print (e)
        await message.reply_text("An Exception occured!")


# Define a regex pattern to match the button text
add_to_group_pattern = re.compile(r"^👥 (Add to group|Добавить в группу|Qrupa əlavə et) 👥$")

@cbot.on_message(filters.regex(add_to_group_pattern) & filters.private & subscribed & user_registered)
async def handle_add_to_group_response(client, message: Message):
    bot = BOT_USERNAME
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add me to your group", url = f"https://t.me/{bot}?startgroup=true")]])
    await message.reply_text("Adding to group...", reply_markup = markup)
