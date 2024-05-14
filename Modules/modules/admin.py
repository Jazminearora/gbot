import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import datetime, time
import pyrostep
import heroku3

from config import  ADMINS as ADMIN_IDS
from Modules import cbot, BOT_ID
from Modules import mongodb as collection
from config import key, HEROKU_API
from helpers.forcesub import is_member
from Modules.modules.register import get_user_name
from helpers.helper import get_total_users, find_language, get_detailed_user_list
from database.premiumdb import get_premium_users, extend_premium_user_hrs
from database.registerdb import remove_user_id

pyrostep.listen(cbot)
os.environ['PROMO_STATUS'] = "True" # by default true

heroku = heroku3.from_key(HEROKU_API)

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
            InlineKeyboardButton("⛓ Referral link", callback_data='referral_admin'),
            InlineKeyboardButton("👑 VIP Users", callback_data='vip_users')
        ],
        [
            InlineKeyboardButton("👥 List of users", callback_data='list_users'),
            InlineKeyboardButton("♿️ Delete inactive", callback_data='delete_inactive')
        ],
        [
            InlineKeyboardButton("🚫 Cancel", callback_data='st_close')
        ]
    ]

home_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]])

failed_users = []

preview_mode = False

# Command handler for /admin
@cbot.on_message(filters.command("admin") & filters.user(ADMIN_IDS))
async def admin_panel(_, message):

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text('Please choose an option:', reply_markup=reply_markup)



@cbot.on_callback_query(filters.regex(r'^subscriptions$'))
async def subscriptions_handler(_, query):
    chat_ids = get_chat_ids()
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add Chat", callback_data="add_chat"),
        InlineKeyboardButton("Delete Chat", callback_data="delete_chat")],
        [InlineKeyboardButton(f"Set {'✅' if os.environ.get('PROMO_STATUS', 'False') else '❌'}", callback_data="set_status")],
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]
    ])
    text = f"Current Chat IDs: {chat_ids}\nStatus: {os.environ.get('PROMO_STATUS', 'False')}"
    await query.message.edit_text(text=text, reply_markup=markup)


@cbot.on_callback_query(filters.regex(r'^add_chat$'))
async def add_chat_handler(client, query):
    await query.message.reply("Enter chat ID to add:")
    chat_id = await pyrostep.wait_for(query.from_user.id)
    try:
        print(chat_id.text)
        chk = await is_member(client, chat_id.text, BOT_ID)
        if chk:
            name = (await cbot.get_chat(chat_id.text)).title
        else:
            await query.message.reply("It seems that it is not a valid chat id. If you believe it is correct, add me to that group/channel as admin first.")
            return
    except Exception as e:
        await query.message.reply(f"An error occured while validating chat id:\n\n{e}")
        return
    add_chat_id(chat_id.text)
    await query.answer(f"Chat: {name} added successfully!", show_alert=True)


@cbot.on_callback_query(filters.regex(r'^delete_chat$'))
async def delete_chat_handler(_, query):
    sk = await query.message.reply("Enter chat ID to delete:")
    chat_id = await pyrostep.wait_for(query.from_user.id)
    delete_chat_id(chat_id.text)
    await query.answer("Chat ID deleted successfully!", show_alert=True)


@cbot.on_callback_query(filters.regex(r'^set_status$'))
async def set_status_handler(_, query):
    promo_status = os.environ.get('PROMO_STATUS') if  os.environ.get('PROMO_STATUS') else "False"
    promo_status = "True" if  promo_status == "False" else "False" # toggle status
    os.environ['PROMO_STATUS'] = promo_status
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add Chat", callback_data="add_chat"),
        InlineKeyboardButton("Delete Chat", callback_data="delete_chat")],
        [InlineKeyboardButton(f"Set {'✅' if promo_status == "True" else '❌'}", callback_data="set_status")],
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]
    ])
    chat_ids = get_chat_ids()
    text = f"Current Chat IDs: {chat_ids}\nStatus: {promo_status}"
    await edit_message(query, text, markup)

async def edit_message(query, text, markup):
    await query.message.edit_text(text, reply_markup=markup)


def add_chat_id(chat_id):
    if 'SUBSCRIPTION' not in os.environ:
        os.environ['SUBSCRIPTION'] = ','.join([chat_id])
    else:
        current_subscription = os.environ['SUBSCRIPTION']
        new_subscription = ','.join([current_subscription, chat_id])
        os.environ['SUBSCRIPTION'] = new_subscription

def delete_chat_id(chat_id):
    if 'SUBSCRIPTION' in os.environ:
        current_subscription = os.environ['SUBSCRIPTION']
        new_subscription = ','.join([sub_id for sub_id in current_subscription.split(',') if sub_id != chat_id])
        if new_subscription:
            os.environ['SUBSCRIPTION'] = new_subscription
        else:
            del os.environ['SUBSCRIPTION']

def get_chat_ids():
    if 'SUBSCRIPTION' in os.environ:
        current_subscription = os.environ['SUBSCRIPTION']
        return current_subscription
    else:
        return ''


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
    await query.message.edit_text(text, reply_markup = home_btn)

@cbot.on_callback_query(filters.regex(r'^statistics$'))
async def statistics_handler(_, query):
    await query.message.edit_text(text="fetching...", reply_markup = home_btn)
    # Get the user counts for each language
    eng_users = get_total_users("English") or 0
    russian_users = get_total_users("Russian") or 0
    azerbejani_users = get_total_users("Azerbejani") or 0
    total_users = eng_users + russian_users + azerbejani_users

    # Get the detailed user list for each language
    eng_detailed_list = get_detailed_user_list("English")
    russian_detailed_list = get_detailed_user_list("Russian")
    azerbejani_detailed_list = get_detailed_user_list("Azerbejani")

    # Format the statistics text using string formatting
    stats_text = (
        "--📊 Total stats of Bot--\n"
        f"👥 Total users: {total_users} \n"
        f"🇬🇧 English users: {eng_users}\n"
        f"🇷🇺 Russian users: {russian_users}\n"
        f"🇦🇿 Azerbejani users: {azerbejani_users}\n\n\n"
        "--👥 𝐏𝐞𝐫𝐬𝐨𝐧𝐚𝐥𝐢𝐳𝐞𝐝 𝐮𝐬𝐞𝐫 𝐥𝐢𝐬𝐭--:\n\n"
    )

    # Add the detailed user list to the statistics text
    if eng_detailed_list:
        stats_text += "--🇬🇧 English--:\n"
        stats_text += await format_detailed_user_list(eng_detailed_list)
        stats_text += "\n\n"
    if russian_detailed_list:
        stats_text += "--🇷🇺 Russian--:\n"
        stats_text += await format_detailed_user_list(russian_detailed_list)
        stats_text += "\n\n"
    if azerbejani_detailed_list:
        stats_text += "--🇦🇿 Azerbejani--:\n"
        stats_text += await format_detailed_user_list(azerbejani_detailed_list)
        stats_text += "\n\n"
    # Edit the message to display the statistics
    await query.message.edit_text(text=stats_text, reply_markup = home_btn)


async def format_detailed_user_list(detailed_list):
    print(detailed_list)
    if detailed_list:
        output = "\n👥 Total Users: {}\n\n".format(detailed_list["Total Users"])
        output += "👩‍♀️ Gender:\n"
        for gender, count in detailed_list["Gender"].items():
            output += "  {0}: {1}\n".format(gender, count)
        output += "\n📆 Age Group:\n"
        for age_group, count in detailed_list["Age Group"].items():
            output += "  {0}: {1}\n".format(age_group, count)
        output += "\n💡 Interest:\n"
        for interest, count in detailed_list["Interest"].items():
            output += "  {0}: {1}\n".format(interest, count)
        return output
    else:
        return "No users found. 😔"
    

@cbot.on_callback_query(filters.regex(r'^vip_users$'))
async def vip_users_handler(_, query):
    premium_user_ids, total_premium_users = get_premium_users()
    if total_premium_users != 0:
        data = {'Premium Users': list(premium_user_ids)}
        filename = 'premium_users.txt'
        save_file(data, filename)
        await query.message.reply_document(
            document="premium_users.txt",
            caption=f"Here is the detailed list of premium users!\n\nTotal Premium users: {total_premium_users}"
        )
    else:
        await query.message.reply_text("There are no premium users at the moment.")

def save_file(data, filename):
    try:
        with open(filename, 'w') as file:
            # Write data to the file
            file.write(str(data))
    except Exception as e:
        print("Error:", e)


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
    confirm_buttons = [
        [
            InlineKeyboardButton("Yes, delete", callback_data='confirm_delete_inactive'),
            InlineKeyboardButton("No, cancel", callback_data='cancel_delete_inactive')
        ]
    ]
    confirm_markup = InlineKeyboardMarkup(confirm_buttons)
    try:
        numb = len(failed_users)
        numbera = numb
    except:
        numbera = 0
    if numbera == 0:
        await query.message.reply_text("No inactive users found at the moment.\n\nNote: For the user ids, when it fails to send the newsletter, user id is considered as inactive users.")
        return
    await query.message.reply_text(text=f"Note: For the user ids, when it fails to send the newsletter, user id is considered as inactive users. \n\nYou are about to delete {numbera} inactive users. This action is irreversible. Are you sure?", reply_markup=confirm_markup)

@cbot.on_callback_query(filters.regex(r'^confirm_delete_inactive$'))
async def confirm_delete_inactive_handler(_, query):
    failed_users = get_failed_users()  # Get the list of failed users
    failed = 0
    success = 0
    start_time = time.time()
    for user_id in failed_users:
        try:
            language = find_language(user_id)
            remove_user_id(None, user_id, language)  # Remove the user ID from the database
            asyncio.sleep(5)
            success += 1
        except Exception as e:
            await query.message.reply_text(f"An exception occured while removing id= {user_id}\n\nException: {e}")
            print("Error in confirm_delete_inactive:", e)
            failed += 1
            pass
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await query.message.edit_text(text=f"Inactive users deleted successfully.\n\nSuccess: {success}\nFailed: {failed}\n\nTime taken: {completed_in}")

def get_failed_users():
    return failed_users  # Return the list of failed users

@cbot.on_callback_query(filters.regex(r'^cancel_delete_inactive$'))
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


@cbot.on_message(filters.command("add_vip", prefixes='/') & filters.user(ADMIN_IDS))
async def add_vip(client, message):
    try:
        command = message.text
        print(command)
        user_id = command.split()[1]
        extend_hrs = int(command.split()[2])
        print(user_id, extend_hrs)
        try:
            # Extend the user's premium hours
            extend_premium_user_hrs(user_id, extend_hrs)
            await message.reply_text(f"Premium hours extended for user {user_id} by {extend_hrs} hours.")
            await cbot.send_message(user_id, f"Received premium membership from admin for {extend_hrs} hours.")
        except Exception as e:
            await message.reply_text(f"Failed to extend premium!\n\nException: {e}")

    except Exception as e:
        await message.reply_text(f"Error: {e}")


@cbot.on_callback_query(filters.regex(r'^st_close$'))
async def close_page(_, query):
    try:
        # Delete the callback message
        await query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)
