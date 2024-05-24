from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
import pyrostep

from .. import cbot
from helpers.forcesub import subscribed, user_registered, anoms_filter
from helpers.translator import translate_async
from helpers.helper import find_language
from Modules.modules.register import get_user_name

pyrostep.listen(cbot)

@cbot.on_message(filters.private & subscribed & user_registered & anoms_filter)
async def get_anonymous(_, message: Message):
    user_id = message.from_user.id
    language = find_language(user_id)
    try:
        command_parts = message.text.split(" ")
        anom_user_id = int(command_parts[1].replace("a", ""))
        name = get_user_name(anom_user_id)
    except ValueError:
        await message.reply(await translate_async("Invalid user id", language))
        return
    if not name:
        await message.reply(await translate_async("Invalid user id", language))
        return
    await message.reply(await translate_async(f"Leave a message here to send {name}. Don't worry, this message will be fully anonymous and your identity will not be revealed.\n\n You can send Text/Photo/Video etc anything you want.", language))
    message = await pyrostep.wait_for(user_id)
    await message.copy(anom_user_id)
    await message.reply(await translate_async("Message sent successfully."))
@cbot.on_callback_query(filters.regex(r'^send_msg$'))
async def send_anom_msg(client, query: CallbackQuery):
    await query.answer("Work in progress", show_alert= True)




    # markup = InlineKeyboardMarkup(
    #     [
    #         [InlineKeyboardButton(text=await translate_async('Good', language), callback_data="send_msg")],
    #         [InlineKeyboardButton(text=await translate_async('Bad 🔙', language), callback_data="guhing")]
    #     ]
    # )   