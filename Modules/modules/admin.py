from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import asyncio
import datetime, time
from config import  ADMINS as ADMIN_IDS
from Modules import cbot, mongodb as collection, BOT_USERNAME
from config import key
from Modules.modules.broadcast import get_failed_users
from helpers.helper import get_total_users, find_language, get_detailed_user_list
from helpers.translator import translate_async
from database.premiumdb import get_premium_users, extend_premium_user_hrs, is_user_premium, calculate_remaining_time
from database.registerdb import remove_user_id


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
        InlineKeyboardButton("🤖Other Commands🤖", callback_data='extra_admin')
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
        InlineKeyboardButton("🔪 Shear Control", callback_data='shear_control')
    ],
    [
        InlineKeyboardButton("🚫 Close", callback_data='st_close')
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
    if detailed_list:
        output = "\n👥 Total Users: {}\n\n".format(detailed_list["Total Users"])
        output += "**👩‍👦 Gender Distribution:**\n"
        for gender, count in detailed_list["Gender"].items():
            if gender == "male":
                gender_emoji = "👨"
            elif gender == "female":
                gender_emoji = "👩"
            else:
                gender_emoji = ""
            output += "- **{} {}:** {}\n".format(gender_emoji, gender, count)
        output += "\n📆 Age Group:\n"
        for age_group, count in detailed_list["Age Group"].items():
            output += "  {0}-  {1}\n".format(age_group, count)
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
        vip_user_list = []
        for user_id in premium_user_ids:
            _, time = is_user_premium(str(user_id))
            vip_time_left = calculate_remaining_time(time)  
            user_link = f"<a href='https://t.me/{BOT_USERNAME}?start=id{user_id}'>{user_id}</a>"
            vip_user_list.append(f"{user_link} - {vip_time_left}")
        
        # Split the message into chunks if it's too long
        max_chars_per_message = 4096
        vip_user_list_chunks = [vip_user_list[i:i + max_chars_per_message] for i in range(0, len(vip_user_list), max_chars_per_message)]
        
        for chunk in vip_user_list_chunks:
            message_text = "\n".join(chunk)
            await query.message.reply_text(
                f"Here is the detailed list of premium users!\n\n{message_text}\n\nTotal Premium users: {total_premium_users}"
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
    processed_data = process_data(raw_data, key)
    # Write user data to a file
    save_to_file(processed_data, filename="Users_Data.txt")

    # Send the file to the admin
    await query.message.reply_document(
        document="Users_Data.txt",
        caption="Here is the detailed list of users!"
    )


@cbot.on_callback_query(filters.regex(r'^delete_inactive$'))
async def delete_inactive_handler(_, query):
    confirm_buttons = [
        [
            InlineKeyboardButton("Yes, delete🚮", callback_data='confirm_delete_inactive'),
            InlineKeyboardButton("No, cancel🙅", callback_data='cancel_delete_inactive')
        ]
    ]
    confirm_markup = InlineKeyboardMarkup(confirm_buttons)
    try:
        failed_users = await get_failed_users
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
    failed_users = await get_failed_users()  # Get the list of failed users
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

@cbot.on_callback_query(filters.regex(r'^cancel_delete_inactive$'))
async def cancel_handler(_, query):
    await query.message.edit_text(text="You canceled the operation.")

@cbot.on_callback_query(filters.regex(r'^st_close$'))
async def close_menu(client, callback_query):
    try:
        # Delete the callback message
        await callback_query.message.delete()
    except Exception as e:
        print("Error in close:", e)
        pass

@cbot.on_callback_query(filters.regex(r'^st_back$'))
async def back_menu(_, query):
    try:
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text('Please choose an option:', reply_markup=reply_markup)  
    except Exception as e:
        print("Error in back:", e)
        pass


@cbot.on_message(filters.command("add_vip") & filters.user(ADMIN_IDS))
async def add_vip(client, message):
    try:
        command = message.text
        if not command.split()[1] or not int(command.split()[2]):
            await message.reply("usage: /add_vip user id extend hrs")
            return
        user_id = int(command.split()[1])
        extend_hrs = int(command.split()[2])
        try: 
            lang = find_language(user_id)
            text =  await translate_async(f"Received premium membership from admin for {extend_hrs} hours.", lang)
            await cbot.send_message(user_id, text)
            await message.reply_text(f"Premium hours extended for user {user_id} by {extend_hrs} hours.")
            # Extend the user's premium hours
            extend_premium_user_hrs(user_id, extend_hrs)
        except Exception as e:
            await message.reply_text(f"Failed to extend premium!\n\nException: {e}")

    except Exception as e:
        await message.reply_text(f"Error: {e}")