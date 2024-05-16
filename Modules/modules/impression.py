from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message as mssg
from pyrogram.errors import RPCError
import pyrostep
from ..modules.advertisement import send_message
import asyncio
from helpers.helper import get_users_list
from telegraph import upload_file
import aiofiles
import json

from .. import cbot, BOT_USERNAME, ADMIN_IDS, msg_collection
from database.prdb import English, Russian, Azerbejani

pyrostep.listen(cbot)
scheduled_message_list = []

async def upload_image(path):
    try:
        link = upload_file(path)
        generated_link = "https://telegra.ph" + "".join(link)
        return generated_link
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None
    

@cbot.on_callback_query(filters.regex(r'^impressions$'))
async def impressions_handler(_, query):
    text = """
🚀 Welcome to the Promo Management System! 🚀

This system helps you manage promotional messages efficiently. Here's a quick guide to the available commands:

📝 /add_msg - Use this command to add a new promotional message to the system.

🗑️ /del_msg - Delete a promotional message from the system using this command.

🔍 /get_msg - Retrieve a list of all available promotional messages in the system with this command.

🔄 /pull_msg - Fetch and update a specific message from the database using this command.

💾 /push_msg - Push the updated message back into the database using this command.

Happy promoting! 🚀✨

"""
    markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(f"Scheduled Promo 🕒", callback_data="st_scheduled"),
     InlineKeyboardButton(f"Auto Promo 🚀", callback_data="st_auto")],
    [InlineKeyboardButton(f"Back 🔙", callback_data="st_back"),
     InlineKeyboardButton(f"Close ❌", callback_data="st_close")]
])
    await query.message.edit_text(text, reply_markup = markup)

@cbot.on_callback_query(filters.regex(r'^st_scheduled$'))
async def scheduled_handler(_, query):

    # Load scheduled promo messages from JSON file
    with open("promo_scheduled.json", "r") as file:
        scheduled_messages = [json.loads(line) for line in file.readlines()]

    # Extract message IDs and durations
    message_ids = [list(msg.keys())[0] for msg in scheduled_messages]
    # Create message text
    text = "**IDs of all saved Messages Scheduled Promo**:\n"
    text += ", ".join(str(id)[8:] for id in message_ids)
    global scheduled_message_list
    if scheduled_message_list:
        text += f"\n\n**Currently scheduled message**:"
        for msg_id, duration, language in scheduled_message_list:
            text += f"\n  • Message ID: {msg_id[8:]}, Duration: {duration}, Language: {language}\n"

    # Create inline keyboard markup
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Schedule Message ⏰", callback_data="st_schedule_msg"),
            InlineKeyboardButton(text="Unschedule message 🗑️", callback_data="st_dlt_msg")
        ],
        [InlineKeyboardButton(text="Get Message 📥", callback_data="st_get_msg")],
        [InlineKeyboardButton(f"Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(f"Close ❌", callback_data="st_close")]
    ])

    # Edit the message with the new text and markup
    await query.message.edit_text(text, reply_markup=markup)

@cbot.on_callback_query(filters.regex(r'^st_get_msg$'))
async def get_msg_ndler(_, query):
    try:
        text = "Enter the message ID you want to get:"
        await query.message.reply_text(text)
        msg_id_input = await pyrostep.wait_for(query.from_user.id)  
        msg_id = int(msg_id_input.text)
        dict_msg = await get_message_details(msg_id)
        if dict_msg:
            msg_text = f"Message ID: {msg_id}\n"
            msg_text += f"Text: {dict_msg.get('text', '')}\n"
            msg_text += f"Button Details: {dict_msg.get('button_details', '')}\n"
            msg_text += f"Photo Link: {dict_msg.get('photo_link', '')}\n"
            msg_text += f"Language: {dict_msg.get('language', '')}"
            await query.message.reply_text(msg_text)
        else:
            await query.message.reply_text("Message not found!")
    except ValueError:
        await query.message.reply_text("Invalid message ID entered!")
    except Exception as e:
        await query.message.reply_text(f"Error occurred!\n{e}")
        
async def get_message_details(msg_id: int) -> dict:
    msg_id_str = f"message_{msg_id}"

    # Check if the message is in the scheduled message list
    for scheduled_msg in scheduled_message_list:
        if scheduled_msg[0] == msg_id_str:
            language = scheduled_msg[2]
            break
    else:
        language = None

    # Load message details from the JSON file
    with open("promo_scheduled.json", "r") as file:
        message_details = {}
        for line in file:
            message_details.update(json.loads(line))

    # Return message details if found
    if msg_id_str in message_details:
        message_details[msg_id_str]["language"] = language
        return message_details[msg_id_str]
    else:
        return {}

def get_messages_list():
    return scheduled_message_list


@cbot.on_callback_query(filters.regex(r'^st_schedule_msg$'))
async def schedule_msg_handler(_, query):
    # Ask user to enter message ID
    text = "Enter the message ID to schedule:"
    sui = await query.message.reply_text(text)

    # Wait for user input
    msg_id_input = await pyrostep.wait_for(query.from_user.id)  
    msg_id = msg_id_input.text

    msg_details = await get_message_details(msg_id)
    if not msg_details:
        await query.message.reply("Message not found, Please recheck message id.")
        return
    # Ask user to choose language
    text = "Choose a language:"
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="English", callback_data=f"lang_{msg_id}_English"),
            InlineKeyboardButton(text="Russian", callback_data=f"lang_{msg_id}_Russian"),
            InlineKeyboardButton(text="Azerbaijani", callback_data=f"lang_{msg_id}_Azerbaijani")
        ]
    ])
    await msg_id_input.delete()
    await sui.edit_text(text, reply_markup=markup)

@cbot.on_callback_query(filters.regex(r'^lang_(.+)_(English|Russian|Azerbaijani)$'))
async def language_handler(_, query):
    msg_id = query.data.split("_")[1]
    msg_id_str = f"message_{msg_id}"
    language = query.data.split("_")[-1]

    # Ask user to enter duration (in hours)
    text = f"Enter the duration (in hours) to send message {msg_id}:"
    await query.message.edit_text(text)

    # Wait for user input
    duration_input = await pyrostep.wait_for(query.from_user.id)  
    try:
        duration = int(duration_input.text)
    except ValueError:
        await query.message.edit_text("You have not entered integer value for lap duration.")
        return

    global scheduled_message_list
    # Save the scheduled message to the local list
    scheduled_message_list.append((msg_id_str, duration, language))
    text = f"Message {msg_id} scheduled successfully! 📝"
    await duration_input.delete()
    await query.message.edit_text(text)
    await sheduled_promo_code(msg_id, msg_id_str, duration, language)

@cbot.on_callback_query(filters.regex(r'^st_dlt_msg$'))
async def unschedule_message_handler(_, query):
    # Ask user to enter the message ID to unschedule
    text = "Enter the message ID to unschedule:"
    suii = await query.message.reply_text(text)

    # Wait for user input
    msg_id_input = await pyrostep.wait_for(query.from_user.id)  
    msg_id = msg_id_input.text

    global scheduled_message_list
    # Check if the message ID exists in the scheduled message list
    for scheduled_msg in scheduled_message_list:
        if scheduled_msg[0] == f"message_{msg_id}":
            # Remove the scheduled message
            scheduled_message_list.remove(scheduled_msg)
            await msg_id_input.delete()
            await suii.edit_text(f"Message {msg_id} unscheduled successfully! 🗑️")
            return

    # If the message ID is not found in the scheduled message list
    await msg_id_input.delete()
    await suii.edit_text(f"Message {msg_id} not found in scheduled messages! ❌")


@cbot.on_message(filters.command("push_msg") & filters.user(ADMIN_IDS))
async def push_msg(_, message):
    try:
        # Get messages from English, Russian, and Azerbejani dictionaries
        english_msgs = dict(English)
        russian_msgs = dict(Russian)
        azerbejani_msgs = dict(Azerbejani)

        # Check if a document with the same _id exists in MongoDB
        existing_doc = msg_collection.find_one({"_id": "messages"})

        if existing_doc:
            # Update the existing document
            msg_collection.update_one({"_id": "messages"}, {
                "$set": {
                    "english": english_msgs,
                    "russian": russian_msgs,
                    "azerbejani": azerbejani_msgs
                }
            })
        else:
            # Insert a new document with the specified _id
            msg_collection.insert_one({
                "_id": "messages",
                "english": english_msgs,
                "russian": russian_msgs,
                "azerbejani": azerbejani_msgs
            })

        await message.reply("Messages saved successfully! 📥")
    except Exception as e:
        await message.reply(f"Error: {e}")

@cbot.on_message(filters.command("pull_msg") & filters.user(ADMIN_IDS))
async def pull_msg(_, message):
    try:
        # Fetch the document with the specified _id from MongoDB
        saved_msgs = msg_collection.find_one({"_id": "messages"})

        if saved_msgs:
            # Update messages from MongoDB
            English.clear()
            Russian.clear()
            Azerbejani.clear()

            English.update(saved_msgs.get("english", {}))
            Russian.update(saved_msgs.get("russian", {}))
            Azerbejani.update(saved_msgs.get("azerbejani", {}))

            await message.reply("Messages pulled and updated successfully! 📤")
        else:
            await message.reply("No saved messages found. ❌")
    except Exception as e:
        await message.reply(f"Error: {e}")


@cbot.on_message(filters.command("add_msg") & filters.user(ADMIN_IDS))
async def add_msg(_, message):
    await cbot.send_message(message.chat.id, "❇ Enter New Message.\nYou can also «Forward» text from another chat or channel.")
    msg = await pyrostep.wait_for(message.chat.id)
    
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

    # Create an inline keyboard for selecting purpose
    keyboard = [
        [
            InlineKeyboardButton("Scheduled Promo", callback_data=f"purpose_scheduled_{lang}_{msg_id}_{chat_id}"),
            InlineKeyboardButton("Auto Promo", callback_data=f"purpose_auto_{lang}_{msg_id}_{chat_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await callback_query.message.edit_reply_markup(reply_markup)
    

@cbot.on_callback_query(filters.regex(r"purpose_(.+)_(.+)_(.+)_(.+)"))
async def purpose_callback(_, callback_query):
    data = callback_query.data.split("_")
    purpose = data[1]
    lang = data[2]
    msg_id = int(data[3])
    chat_id = int(data[4])

    metadata = await cbot.get_messages(chat_id, msg_id)
    reply_markup = metadata.reply_markup
    button_details = []
    if reply_markup:
        # Extract button details from the reply markup
        for row in reply_markup.inline_keyboard:
            for button in row:
                button_details.append({
                    'btn_text': button.text,
                    'btn_url': button.url if button.url else None
                })

    if metadata.photo:
        # Download the photo
        photo_path = await cbot.download_media(message=metadata, file_name=f"image/photo1.jpg")
        
        # Upload the photo to Telegraph and get the link
        photo_link = await upload_image(photo_path)
    else:
        photo_link = None

    # Store the message details
    message_details = {
        "text": metadata.caption if photo_link else metadata.text,
        "button_details": button_details if button_details else None,
        "photo_link": photo_link
    }

    # Save message details based on purpose and language
    if purpose == "scheduled":
        # Save message details for scheduled promo in JSON format
        with open(f"promo_scheduled.json", "a") as file:
            json.dump({f"message_{metadata.id}": message_details}, file)
            file.write("\n")
    else:
        if lang == "ENGLISH":
            English[f"message_{metadata.id}"] = message_details
        elif lang == "RUSSIAN":
            Russian[f"message_{metadata.id}"] = message_details
        elif lang == "AZERBAIJANI":
            Azerbejani[f"message_{metadata.id}"] = message_details

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
        await message.reply_document('promo_scheduled.json')
        # Send the file as a message
        await message.reply_document("all_messages.txt")

    except Exception as e:
        await message.reply(f"Error: {str(e)}")

@cbot.on_message(filters.command("del_msg") & filters.user(ADMIN_IDS))
async def del_msg(_, message):
    await cbot.send_message(message.chat.id, "Enter the message ID to delete.")
    msg_id = await pyrostep.wait_for(message.chat.id)
    
    try:
        if msg_id.text.startswith("message_"):
            msg_id = msg_id.text[8:]
        else:
            msg_id = int(msg_id.text)
    except ValueError:
        await message.reply("Invalid message ID. Please enter a valid ID.")
        return
    
    for lang in [English, Russian, Azerbejani]:
        if f"message_{msg_id}" in lang:
            del lang[f"message_{msg_id}"]
            us = await delete_scheduled_message(f"message_{msg_id}")
            text = "Message deleted from file successfully."
            if us:
                text += f"\nAlso removed message from currently scheduled messages."
            await message.reply(text)
            return
    await message.reply("Message not found.")

async def delete_scheduled_message(msg_id):
    global scheduled_message_list
    for i, (id, duration, language) in enumerate(scheduled_message_list):
        if id == msg_id:
            del scheduled_message_list[i]
            return True
    return False


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##


async def sheduled_promo_code(msg_id: int, msg_id_str: str, duration: int, language: str) -> None:
    """
    Send scheduled promo codes to users.
    """
    print("called", )
    while True:
        print("called2", msg_id, duration)
        try:
            messages_list = get_messages_list()
            if not messages_list:
                await asyncio.sleep(60)  # sleep for 1 minute before checking again
                continue

            msg_details = await get_message_details(msg_id)
            if not msg_details:
                break  # break the loop if the message is no longer in the list

            msg_text = msg_details.get("text")
            inline_btn = msg_details.get("button_details")
            reply_markup = None
            if inline_btn:
                keyboard = [InlineKeyboardButton(btn['btn_text'], url=btn['btn_url']) for btn in inline_btn]
                reply_markup = InlineKeyboardMarkup([keyboard])

            photo_link = msg_details.get("photo_link")
            lang = language

            users = get_users_list(lang)
            for user in users:
                await send_message(user, msg_id, msg_text, reply_markup, photo_link)

            await asyncio.sleep(int(duration) * 60 * 60)  # sleep for the specified duration in hrs

        except Exception as e:
            print(f"Error in scheduled promo code: {e}")
            await asyncio.sleep(60)  # sleep for 1 minute before retrying

        # check if the message is still in the list
        messages_list = get_messages_list()
        if msg_id_str not in [msg[0] for msg in messages_list]:
            print("breaking")
            break  # break the loop if the message is no longer in the list