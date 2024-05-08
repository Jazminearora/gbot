from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message as mssg
from pyrogram.errors import RPCError
import pyrostep
import os
from telegraph import upload_file
import aiofiles

from .. import cbot, BOT_USERNAME, ADMIN_IDS
from database.prdb import English, Russian, Azerbejani

pyrostep.listen(cbot)


async def upload_image(path):
    try:
        link = upload_file(path)
        generated_link = "https://telegra.ph" + "".join(link)
        return generated_link
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None
    

@cbot.on_message(filters.command("add_msg") & filters.user(ADMIN_IDS))
async def add_msg(_, message):
    await cbot.send_message(message.chat.id, "❇ Enter New Message.\nYou can also «Forward» text from another chat or channel.")
    msg = await pyrostep.wait_for(message.chat.id)
    
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
    
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("English", callback_data=f"lang_ENGLISH_{msg_id}_{chat_id}"),
            InlineKeyboardButton("Russian", callback_data=f"lang_RUSSIAN_{msg_id}_{chat_id}"),
            InlineKeyboardButton("Azerbejani", callback_data=f"lang_AZERBAIJANI_{msg_id}_{chat_id}")
        ]
    ])
    
    await callback_query.message.edit_text("Choose a language to save the message:", reply_markup=markup)

@cbot.on_callback_query(filters.regex(r"lang_(.+)_(.+)_(.+)"))
async def lang_callback(_, callback_query):
    data = callback_query.data.split("_")
    lang = data[1]
    msg_id = int(data[2])
    chat_id = int(data[3])
    
    metadata = await cbot.get_messages(chat_id, msg_id)
    
    if metadata.photo:
        # Download the photo
        photo_path = await cbot.download_media(message=metadata, file_name=f"image/photo1.jpg")
        
        # Upload the photo to Telegraph and get the link
        photo_link = await upload_image(photo_path)
    else:
        photo_link = None
    # Store the photo link along with the text and markup
    if lang == "ENGLISH":
        English[f"message_{metadata.id}"] = {
            "text": metadata.caption if photo_link else metadata.text,
            "reply_markup": metadata.reply_markup,
            "photo_link": photo_link
        }
    elif lang == "RUSSIAN":
        Russian[f"message_{metadata.id}"] = {
            "text": metadata.caption if photo_link else metadata.text,
            "reply_markup": metadata.reply_markup,
            "photo_link": photo_link
        }
    elif lang == "AZERBAIJANI":
        Azerbejani[f"message_{metadata.id}"] = {
            "text": metadata.text,
            "text": metadata.caption if photo_link else metadata.text,
            "photo_link": photo_link
        }
    await callback_query.answer("Message saved.", show_alert=True)
    await callback_query.message.delete()

@cbot.on_callback_query(filters.regex(r"add_(.+)_(.+)"))
async def add_callback(_, callback_query):
    await callback_query.message.delete()
    data = callback_query.data.split("_")
    msg_id = int(data[1])
    chat_id = int(data[2])
    metadata = await cbot.get_messages(chat_id, msg_id)

    await cbot.send_message(callback_query.message.chat.id, f"❇ Enter data for the URL/SHARE-button.\n\n➠ For example to create «Share» button with the link to our help bot enter:\nShare\nhttps://t.me/share/url?url=t.me/{BOT_USERNAME}\n\nℹ Data shall go in TWO LINES:\nBUTTON TITLE\nURL/Share address")
    await pyrostep.register_next_step(callback_query.from_user.id, wait_for_message, kwargs={"metadata": metadata})

    # await _process_button_addition(metadata, callback_query, title, url)


async def wait_for_message(_, msg: mssg, metadata):
    try:
        title, url = msg.text.split("\n")
    except ValueError:
        await msg.reply(f"Please enter data in correct format (two lines example: \nShare\nhttps://t.me/share/url?url=t.me/{BOT_USERNAME}.")
        await pyrostep.register_next_step(msg.from_user.id, wait_for_message, kwargs={"metadata": metadata})
        return
    try:
        keyboard = metadata.reply_markup
        if keyboard:
            new_keyboard = keyboard.inline_keyboard
        else:
            new_keyboard = []
        new_keyboard.append([InlineKeyboardButton(title, url=url)])
        keyboard = InlineKeyboardMarkup(new_keyboard)
        sent = await metadata.copy(chat_id=int(msg.chat.id))
        try:
            await cbot.edit_message_reply_markup(chat_id=sent.chat.id, message_id=sent.id, reply_markup=keyboard)
        except RPCError as r:
            pass
        save_button = InlineKeyboardButton("Save", callback_data=f"save_{sent.id}_{sent.chat.id}")
        add_button = InlineKeyboardButton("➕ Inline Button", callback_data=f"add_{sent.id}_{sent.chat.id}")
        reply_markup = InlineKeyboardMarkup([[save_button, add_button]])
        await cbot.send_message(msg.chat.id, "Do you want to add another button?", reply_markup=reply_markup)

    except RPCError as e:
        print(f"Error editing message: {e}")
        return


@cbot.on_message(filters.command("get_msg") & filters.user(ADMIN_IDS))
async def get_msg(_, message):
    all_messages = {
        'english': English,
        'russian': Russian,
        'azerbaijani': Azerbejani
    }

    try:
        # Create a temporary file
        async with aiofiles.open('all_messages.txt', 'w') as f:
            for lang, msg in all_messages.items():
                await f.write(f"{lang}: {msg}\n")

        # Send the file as a message
        await message.reply_document("all_messages.txt")

        # Delete the file
        os.remove("all_messages.txt")

    except Exception as e:
        await message.reply(f"Error: {str(e)}")
