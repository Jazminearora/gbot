from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram import filters, Client
from pyrogram.errors import RPCError
import pyrostep

from .. import cbot, LOG_GROUP, BOT_USERNAME, ADMIN_IDS
from helpers.filters import subscribed, user_registered
from helpers.helper import find_language
from helpers.translator import translate_async

pyrostep.listen(cbot)

@cbot.on_message(filters.command("support") & filters.private & subscribed & user_registered)
async def support_handler(client: Client, message: Message):
    user_id = message.from_user.id
    lang = find_language(user_id)
    await message.reply(await translate_async("Drop a text message here:", lang))
    try:
        incoming = await pyrostep.wait_for(user_id, timeout= 600)
        message = incoming.text
        if not message:
            await incoming.reply(await translate_async("Please send a text message only.", lang), quote=True)
            return
    except TimeoutError:
        await message.reply(await translate_async("Timeout! Please use command again.", lang))
    #keyboard for answer and ignore buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Answer 🧩", callback_data=f"answer_support_{user_id}"),
         InlineKeyboardButton("Ignore 😏", callback_data="ignore_support")]
    ])  
    user_link = f"<a href='https://t.me/{BOT_USERNAME}?start=id{user_id}'>{user_id}</a>"
    await client.send_message(int(LOG_GROUP), text= f"""
🆘SUPPORT🆘
#support #question
                              
**User:** {user_link}
**Message:** {message}
""", reply_markup= keyboard)
    

#callback code for answer button
@cbot.on_callback_query(filters.regex("answer_support"))
async def answer_support(client: Client, callback_query: CallbackQuery):
    #check if clicker is admin or not
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("You are not authorized to answer support queries.", show_alert=True)
        return
    user_id = callback_query.data.split("_")[2]
    #ask to enter the message to answer
    await callback_query.message.reply("Enter your answer:")
    try:
        incoming = await pyrostep.wait_for(callback_query.from_user.id, timeout= 600)
        answer = incoming.text
        if not answer:
            await callback_query.message.reply("Please enter a valid answer text only.")
            return
    except TimeoutError:
        await callback_query.message.reply("Timeout! Please use button again.")
    try:
        #notify answer to the user id
        await client.send_message(int(user_id), f"📨 Support: {answer}")
        await callback_query.message.reply("Answer sent successfully!")
    except (RPCError, Exception) as e:
        await callback_query.message.reply(f"Error while sending answer: {e}")

# callback of ignore button
@cbot.on_callback_query(filters.regex("ignore_support"))
async def ignore_support(client: Client, callback_query: CallbackQuery):
    #check if clicker is admin or not
    if callback_query.from_user.id not in ADMIN_IDS:
        await callback_query.answer("You are not authorized to ignore support queries.", show_alert=True)
        return
    #delete t message and sw alert
    await callback_query.answer("Ignored successfully!", show_alert=True)
    await callback_query.message.delete()