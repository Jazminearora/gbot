import os
from pyrogram import filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import asyncio
import datetime, time
import pyrostep

from config import  ADMINS as ADMIN_IDS
from Modules import cbot, logger, BOT_USERNAME
from Modules import mongodb as collection
from config import key
from helpers.helper import get_total_users, get_users_list, find_language, get_detailed_user_list
from database.premiumdb import get_premium_users, extend_premium_user_hrs
from database.registerdb import remove_user_id
from database.referdb import create_refer_program, delete_refer_program, get_refer_programs_data

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

@cbot.on_callback_query(filters.regex(r'^newsletter$'))
async def newsletter_handler(_, query):


    global preview_mode


    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Preview Mode On", callback_data='preview_on'),
            InlineKeyboardButton("Preview Mode Off", callback_data='preview_off'),
        ]
    ])
    await query.message.reply_text(f'Preview mode: {preview_mode}\n\nPlease choose a preview mode:', reply_markup=reply_markup)

@cbot.on_callback_query(filters.regex(r'^preview_(on|off)$'))
async def preview_handler(_, query):
    global preview_mode
    if query.data == 'preview_on':
        preview_mode = True
    else:
        preview_mode = False
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
    await query.message.reply_text(text="Please choose the language for the newsletter recipients:", reply_markup=lang_markup)


async def wait_for_10_seconds():
    await asyncio.sleep(10)
    return True

@cbot.on_callback_query(filters.regex(r'^newsletter_(English|Russian|Azerbejani)$'))
async def newsletter_language_handler(_, query):
    lang = query.data.split('_')[1]
    await query.message.edit_text(text="Enter the newsletter message:")
    newsletter_msg = await pyrostep.wait_for(query.from_user.id)
    if newsletter_msg:
        if preview_mode:
            await newsletter_msg.forward(chat_id=int(query.from_user.id))
        else:
            await newsletter_msg.copy(chat_id=int(query.from_user.id))
        await cbot.send_message(query.from_user.id, text="Do you want to broadcast this message? (y/n)")
        confirmation = await pyrostep.wait_for(query.from_user.id)
        confirmation_text = confirmation.text
        if confirmation_text == 'y':
            global broadcasting_in_progress
            broadcasting_in_progress = True
            users = get_users_list(lang)
            stop_broadcast_button = InlineKeyboardButton("Stop Broadcasting", callback_data="stop_broadcast")
            stop_broadcast_markup = InlineKeyboardMarkup([[stop_broadcast_button]])
            sts_msg = await cbot.send_message(query.from_user.id, text="Starting process of Sending newsletter in 10 seconds...", reply_markup=stop_broadcast_markup)

            # Wait for 10 seconds
            if await wait_for_10_seconds():
                done = 0
                failed = 0
                success = 0
                start_time = time.time()
                total_users = len(users)
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
                await cbot.send_message(query.from_user.id, text="Broadcasting cancelled by admin.")
        elif confirmation_text == 'n':
            await cbot.send_message(query.from_user.id, text="Broadcast cancelled by admin.")
        else:
            await cbot.send_message(query.from_user.id, text="Invalid response. Please enter y or n.")
    else:
        await cbot.send_message(query.from_user.id, text="Newsletter message not received. Please try again.")
@cbot.on_callback_query(filters.regex(r'^stop_broadcast$'))
async def stop_broadcasting_handler(_, query):
    global broadcasting_in_progress
    broadcasting_in_progress = False
    await query.message.edit_text(text="Broadcasting stopped.")

async def send_newsletter(user_id, message):
    global preview_mode
    try:
        if preview_mode:
            await message.forward(chat_id=int(user_id))
        else:
            await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_newsletter(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Deactivated")
        failed_users.append(user_id)
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Blocked")
        failed_users.append(user_id)
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Invalid ID")
        failed_users.append(user_id)
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        failed_users.append(user_id)
        return 500

@cbot.on_callback_query(filters.regex(r'^subscriptions$'))
async def subscriptions_handler(_, query):
    await query.message.edit_text(text="You selected Subscriptions.")

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


# Callback handler for referral_admin
@cbot.on_callback_query(filters.regex('referral_admin'))
async def referral_admin(_, callback_query):
    # Get the current active refer programs
    programs = await get_refer_programs_data()
    
    # Create a string to display the program names and total points
    program_str = ""
    for index, program in enumerate(programs, start=1):
        program_name = program['name']
        program_id = program['id']
        total_points = program['points']
        refer_link = f"https://t.me/{BOT_USERNAME}?start=r{program_id}"
        
        program_details = (
            f"🔹 {index}. Program name: {program_name}\n"
            f"     🆔 ID: {program_id}\n"
            f"     🔢 Total Points: {total_points}\n"
            f"     🔗 Refer link: {refer_link}\n\n"
        )
        program_str += program_details
    
    # Create an InlineKeyboardMarkup with buttons for adding and deleting programs
    program_buttons = [
        [
            InlineKeyboardButton("📊 Add program", callback_data='add_program'),
            InlineKeyboardButton("🗑️ Delete program", callback_data='delete_program')
        ]
    ]
    program_markup = InlineKeyboardMarkup(program_buttons)
    
    # Send a message with the program details and the program buttons
    await cbot.send_message(callback_query.from_user.id, f"Current active refer programs:\n\n{program_str}", reply_markup=program_markup)

# Callback handler for add_program
@cbot.on_callback_query(filters.regex('add_program'))
async def add_program(_, callback_query):
    try:
        # Ask the admin to enter the program name
        await callback_query.message.reply_text(text="Please enter the new program name:")
        program_name = await pyrostep.wait_for(callback_query.from_user.id)
        
        # Ask the admin to enter the admin and chat IDs
        await callback_query.message.reply_text(text="Please enter the users/chat IDs where I will report on new joining. Provide one ID per line:")
        admin_chat_ids_input = await pyrostep.wait_for(callback_query.from_user.id)
        try:
            # Split the input by newline character to create a list of IDs
            admin_list = [(id) for id in admin_chat_ids_input.text.split('\n') if id.strip()]
        except ValueError:
            await callback_query.message.reply_text("Its seems you didn't provided admins id in correct format.")          
        print(admin_list)
    except TimeoutError:
        await callback_query.message.reply_text("OHOO, Timeout error! Please retry again.")
        return
    try:
        if not admin_list or program_name.text:
            await callback_query.message.reply_text("OHOO, Timeout error! Please retry again.")
            return
        # Create the new refer program
        program_id = await create_refer_program(admin_ids= admin_list, promotion_name= program_name.text)
    except Exception as r:
        await callback_query.message.edit_text(text=f"An error occured!\n\n{r}")
    # Send a message to the admin with the program ID
    await callback_query.message.reply_text(f"Refer program '{program_name.text}' created with ID {program_id}")

# Callback handler for delete_program
@cbot.on_callback_query(filters.regex('delete_program'))
async def delete_program(_, callback_query):


    # Ask the admin to enter the program ID
    await callback_query.message.reply_text(text="Please enter the program ID:")
    program_id = await pyrostep.wait_for(callback_query.from_user.id)
    # Delete the refer program with the given ID
    await delete_refer_program(int(program_id.text))
    # Send a message to the admin with the program ID
    await callback_query.message.reply_text(f"Refer program with ID {program_id.text} deleted")