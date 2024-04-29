import os
from pyrogram import filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import asyncio
import datetime, time
import pyrostep

from config import  ADMINS as ADMIN_IDS
from Modules import cbot, logger
from Modules import mongodb as collection
from config import key
from helpers.helper import get_total_users, get_users_list

pyrostep.listen(cbot)
broadcasting_in_progress = False


buttons = [
        [
            InlineKeyboardButton("📥 Newsletter", callback_data='newsletter'),
            InlineKeyboardButton("✏️ Subscriptions", callback_data='subscriptions')
        ],
        [
            InlineKeyboardButton("👁️‍🗨️ Impressions", callback_data='impressions'),
            InlineKeyboardButton("📊 Statistics", callback_data='statistics')
        ],
        [
            InlineKeyboardButton("⛓ Referral link", callback_data='referral'),
            InlineKeyboardButton("👑 VIP Users", callback_data='vip_users')
        ],
        [
            InlineKeyboardButton("👥 List of users", callback_data='list_users'),
            InlineKeyboardButton("♿️ Delete inactive", callback_data='delete_inactive')
        ],
        [
            InlineKeyboardButton("🚫 Cancel", callback_data='cancel')
        ]
    ]

home_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]])


# Command handler for /admin
@cbot.on_message(filters.command("admin") & filters.user(ADMIN_IDS))
async def admin_panel(_, message):

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text('Please choose an option:', reply_markup=reply_markup)

@cbot.on_callback_query(filters.regex(r'^newsletter$'))
async def newsletter_handler(_, query):
    await query.message.edit_text(text="Select the language for the newsletter:")
    lang_buttons = [
        [
            InlineKeyboardButton("English", callback_data='newsletter_English'),
            InlineKeyboardButton("Russian", callback_data='newsletter_Russian'),
            InlineKeyboardButton("Azerbejani", callback_data='newsletter_Azerbejani'),
        ],
        [
            InlineKeyboardButton("Cancel", callback_data='cancel')
        ]
    ]
    lang_markup = InlineKeyboardMarkup(lang_buttons)
    await query.message.edit_text(text="Select the language for the newsletter:", reply_markup=lang_markup)

@cbot.on_callback_query(filters.regex(r'^newsletter_(English|Russian|Azerbejani)$'))
async def newsletter_language_handler(_, query):
    lang = query.data.split('_')[1]
    await query.message.edit_text(text="Enter the newsletter message:")
    newsletter_msg = await pyrostep.wait_for(query.from_user.id)
    if newsletter_msg:
        global broadcasting_in_progress
        broadcasting_in_progress = True
        users = get_users_list(lang)
        stop_broadcast_button = KeyboardButton("Stop Broadcasting")
        stop_broadcast_markup = ReplyKeyboardMarkup([[stop_broadcast_button]], resize_keyboard=True, one_time_keyboard= True)
        sts_msg = await cbot.send_message(query.from_user.id, text="Sending newsletter in 10 seconds...", reply_markup= stop_broadcast_markup)
        done = 0
        failed = 0
        success = 0
        start_time = time.time()
        total_users = len(users)
        asyncio.sleep(10)
        for user in users:
            if broadcasting_in_progress:
                sts = await send_newsletter(user, newsletter_msg)
                if sts == 200:
                    success += 1
                else:
                    failed += 1
                done += 1
                if not done % 20:
                    await sts_msg.edit(
                        text=f"Sending newsletter...\nTotal users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}"
                    )
            else:
                break
        if broadcasting_in_progress:
            completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
            await cbot.send_message(query.from_user.id,
                text=f"Newsletter sent successfully!\nCompleted in {completed_in}\nTotal users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}"
            )
        else:
            await cbot.send_message(query.from_user.id, text="Broadcasting stopped by admin.")
    else:
        await cbot.send_message(query.from_user.id, text="Newsletter message not received. Please try again.")

@cbot.on_callback_query(filters.regex(r'^stop_broadcasting$'))
async def stop_broadcasting_handler(_, query):
    global broadcasting_in_progress
    broadcasting_in_progress = False
    await query.message.edit_text(text="Broadcasting stopped.")

async def send_newsletter(user_id, message):
    try:
        await message.forward(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_newsletter(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Deactivated")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Blocked")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Invalid ID")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500

@cbot.on_callback_query(filters.regex(r'^subscriptions$'))
async def subscriptions_handler(_, query):
    await query.message.edit_text(text="You selected Subscriptions.")

@cbot.on_callback_query(filters.regex(r'^impressions$'))
async def impressions_handler(_, query):
    await query.message.edit_text(text="You selected Impressions.")

@cbot.on_callback_query(filters.regex(r'^statistics$'))
async def statistics_handler(_, query):
    # Get the user counts for each language
    eng_users = get_total_users("English") or 0
    russian_users = get_total_users("Russian") or 0
    azerbejani_users = get_total_users("Azerbejani") or 0
    total_users = eng_users + russian_users + azerbejani_users

    # Format the statistics text using string formatting
    stats_text = (
        "--Total stats of Bot--\n"
        f"Total users: {total_users} \n"
        f"English users: {eng_users}\n"
        f"Russian users: {russian_users}\n"
        f"Azerbejani users: {azerbejani_users}"
    )
    # Edit the message to display the statistics
    await query.message.edit_text(text=stats_text, reply_markup = home_btn)

    
@cbot.on_callback_query(filters.regex(r'^referral$'))
async def referral_handler(_, query):
    await query.message.edit_text(text="You selected Referral link.")

@cbot.on_callback_query(filters.regex(r'^vip_users$'))
async def vip_users_handler(_, query):
    await query.message.edit_text(text="You selected VIP Users.")

@cbot.on_callback_query(filters.regex(r'^st_close$'))
async def close_page(_, query):
    try:
        # Delete the callback message
        await query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

@cbot.on_callback_query(filters.regex(r'^st_back$'))
async def back_page(_, query):
    try:
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text('Please choose an option:', reply_markup=reply_markup)
    except Exception as e:
        print("Error in close_profile:", e)

# Function to fetch user data from MongoDB
def get_user_data(collection):
    document = collection.find_one({})
    if document:
        return document
    else:
        return {}

def process_data(data, key):
    readable_data = {}
    for language, details in data[key].items():
        readable_data[language] = {}
        for field, users in details.items():
            readable_data[language][field] = ', '.join(map(str, users))
    return readable_data

# Function to write user data to a file
def save_to_file(data, filename):
    with open(filename, 'w') as file:
        for language, details in data.items():
            file.write(f'Language: {language}\n')
            for field, users in details.items():
                file.write(f'  {field}: {users}\n')
            file.write('\n')

# Callback handler for 'List of users' option
@cbot.on_callback_query(filters.regex(r'^list_users$'))
async def list_users_handler(_, query):
    # Retrieve user data from MongoDB collections
    raw_data = collection.find_one({key: {"$exists": True}})
    print(raw_data)
    processed_data = process_data(raw_data, key)
    # Write user data to a file
    save_to_file(processed_data, filename="Users_Data.txt")

    # Send the file to the admin
    await query.message.reply_document(
        document="Users_Data.txt",
        caption="Here is the detailed list of users!"
    )

    # Remove the file after sending it
    os.remove("Users_Data.txt")
@cbot.on_callback_query(filters.regex(r'^delete_inactive$'))
async def delete_inactive_handler(_, query):
    await query.message.edit_text(text="You selected Delete inactive.")

@cbot.on_callback_query(filters.regex(r'^cancel$'))
async def cancel_handler(_, query):
    await query.message.edit_text(text="You canceled the operation.")

@cbot.on_callback_query(filters.regex(r'^st_close$'))
async def close_menu(client, callback_query):
    try:
        # Delete the callback message
        await callback_query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

@cbot.on_callback_query(filters.regex(r'^st_back$'))
async def back_menu(_, query):
    try:
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text('Please choose an option:', reply_markup=reply_markup)  
    except Exception as e:
        print("Error in back_profile:", e)