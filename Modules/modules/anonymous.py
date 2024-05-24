from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import RPCError
import pyrostep

from .. import cbot
from helpers.forcesub import subscribed, user_registered, anoms_filter
from helpers.translator import translate_async
from helpers.helper import find_language
from Modules.modules.register import get_user_name

pyrostep.listen(cbot)

@cbot.on_message(filters.private & subscribed & user_registered & anoms_filter)
async def get_anonymous(client, message: Message):
    user_id = message.from_user.id
    language = find_language(user_id)
    anom_lang = find_language(user_id)
    try:
        command_parts = message.text.split(" ")
        anom_user_id = int(command_parts[1].replace("a", ""))
        name = await get_user_name(anom_user_id)
    except ValueError:
        await message.reply(await translate_async("Invalid user id", language))
        return
    if not name:
        await message.reply(await translate_async("Invalid user id", language))
        return
    await message.reply(await translate_async(f"Leave a message here to send {name}. Don't worry, this message will be fully anonymous and your identity will not be revealed.\n\n You can send Text/Photo/Video etc anything you want.", language))
    message = await pyrostep.wait_for(user_id)
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=await translate_async('Answer ✅', language), callback_data=f"answer_msg_{user_id}"),
            InlineKeyboardButton(text=await translate_async('Block ❌', language), callback_data=f"block_msg_{user_id}")]
        ]
    )       
    try:
        await client.send_message(anom_user_id, f"{await translate_async(f"A new anonymous message recieved from ID{user_id}", anom_lang)}", reply_markup = markup)
        await message.copy(anom_user_id)
        await message.reply(await translate_async("Message sent successfully.", language))
    except RPCError as e:
        await message.reply(await translate_async(f"Error: {e}", language))

@cbot.on_callback_query(filters.regex(r"answer_msg_(\d+)"))
async def answer_msg(client, callback_query: CallbackQuery):
    anom_user_id = int(callback_query.data.split("_")[2])
    user_id = callback_query.from_user.id
    language = find_language(user_id)
    await callback_query.message.reply(await translate_async("Enter your answer:", language))
    await callback_query.message.delete()
    answer = await pyrostep.wait_for(user_id)
    markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=await translate_async('Answer ✅', language), callback_data=f"answer_msg_{anom_user_id}"),
            InlineKeyboardButton(text=await translate_async('Block ❌', language), callback_data=f"block_msg_{anom_user_id}")]
        ]
    )
    await client.send_message(anom_user_id, await translate_async("You got a response:", language), reply_markup=markup)
    await answer.copy(anom_user_id)
    await answer.reply(await translate_async("Answer sent successfully.", language))


    # markup = InlineKeyboardMarkup(
    #     [
    #         [InlineKeyboardButton(text=await translate_async('Good', language), callback_data="send_msg")],
    #         [InlineKeyboardButton(text=await translate_async('Bad 🔙', language), callback_data="guhing")]
    #     ]
    # )   