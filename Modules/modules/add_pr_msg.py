from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import RPCError
import pyrostep

from .. import cbot, BOT_USERNAME, ADMIN_IDS
from database.prdb import PROMO_MSG
import os

pyrostep.listen(cbot)

@cbot.on_message(filters.command("add_msg") & filters.user(ADMIN_IDS))
async def add_msg(_, message):
    await cbot.send_message(message.chat.id, "❇ Enter New Message.\nYou can also «Forward» text from another chat or channel.")
    msg = await pyrostep.wait_for(message.chat.id)
    print(msg)
    
    if msg.forward_from:
        await msg.forward(chat_id=int(message.chat.id))
        save_button = InlineKeyboardButton("Save", callback_data=f"save_{msg.id}_{msg.forward_from.id}")
        keyboard = InlineKeyboardMarkup([[save_button]])
        await cbot.send_message(message.chat.id, "Do you want to save the above forwarded message?", reply_markup=keyboard)
    else:
        await msg.copy(chat_id=int(message.chat.id))
        save_button = InlineKeyboardButton("Save", callback_data=f"save_{msg.id}_{msg.chat.id}")
        add_button = InlineKeyboardButton("➕ Inline Button", callback_data=f"add_{msg.id}_{msg.chat.id}")
        keyboard = InlineKeyboardMarkup([[save_button, add_button]])
        try:
            await message.reply_text("Please choose a button from below.", reply_markup=keyboard)
        except RPCError as e:
            print(f"Error sending message: {e}")
            return

@cbot.on_callback_query(filters.regex(r"save_(.+)_(.+)"))
async def save_callback(_, callback_query):
    data = callback_query.data.split("_")
    msg_id = int(data[1])
    chat_id = int(data[2])
    metadata = await cbot.get_messages(chat_id, msg_id)
    PROMO_MSG.append(metadata)
    await callback_query.answer("Message saved.")

@cbot.on_callback_query(filters.regex(r"add_(.+)_(.+)"))
async def add_callback(_, callback_query):
    await callback_query.message.delete()
    data = callback_query.data.split("_")
    msg_id = int(data[1])
    chat_id = int(data[2])
    metadata = await cbot.get_messages(chat_id, msg_id)

    await cbot.send_message(callback_query.message.chat.id, f"❇ Enter data for the URL/SHARE-button.\n\n➠ For example to create «Share» button with the link to our help bot enter:\nShare\nhttps://t.me/share/url?url=t.me/{BOT_USERNAME}\n\nℹ Data shall go in TWO LINES:\nBUTTON TITLE\nURL/Share address")
    msg = await pyrostep.wait_for(callback_query.message.chat.id)

    if msg.text:
        title, url = msg.text.split("\n")
        try:
            keyboard = metadata.reply_markup
            if keyboard:
                new_keyboard = keyboard.inline_keyboard
            else:
                new_keyboard = []
            print(metadata.chat.id, ":", metadata.id)
            new_keyboard.append([InlineKeyboardButton(title, url=url)])
            keyboard = InlineKeyboardMarkup(new_keyboard)
            sent = await metadata.copy(chat_id=int(callback_query.message.chat.id))
            message_id = sent.id
            try:
                 # update reply markup in metadata
                updated_metadata = await cbot.edit_message_reply_markup(chat_id=metadata.chat.id, message_id=message_id, reply_markup=keyboard)
            except RPCError as e:
                print(f"Error editing message: {e}")
            #send the upated msg with new inline button
            updated_metadata.copy(callback_query.message.chat.id)
            save_button = InlineKeyboardButton("Save", callback_data=f"save_{updated_metadata.id}_{updated_metadata.chat.id}")
            add_button = InlineKeyboardButton("➕ Inline Button", callback_data=f"add_{updated_metadata.id}_{updated_metadata.chat.id}")
            reply_markup = InlineKeyboardMarkup([[save_button, add_button]])
            await cbot.send_message(callback_query.message.chat.id, "Do you want to add another button?", reply_markup=reply_markup)

        except RPCError as e:
            print(f"Error editing message: {e}")
            return

@cbot.on_message(filters.command("get_msg") & filters.user(ADMIN_IDS))
async def get_msg(_, message):
    # Create a new file with PROMO_MSG content
    with open("promo_msg.txt", "w") as f:
        f.write(PROMO_MSG)

    # Send the file as a message
    await message.reply_document("promo_msg.txt")

    # Remove the file from the file system
    os.remove("promo_msg.txt")