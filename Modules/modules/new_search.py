import asyncio
from datetime import datetime
import time
import re
import apscheduler.schedulers.asyncio as aps
from pyrogram import filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup

from helpers.forcesub import subscribed, user_registered
from helpers.helper import find_language, get_age_group, get_gender, get_interest
from helpers.translator import translate_async
from langdb.get_msg import get_reply_markup, interlocutor_normal_message, interlocutor_vip_message
from Modules import cbot
from Modules.modules.register import get_user_name
from database.premiumdb import save_premium_user, vip_users_details, is_user_premium


# Create a scheduler
scheduler = aps.AsyncIOScheduler()

# List to store users searching for an interlocutor
searching_users = []
searching_premium_users = []

# List to store pairs of users for chatting
chat_pairs = []

# Dictionary to store last message timestamps for each user
message_timestamps = {}

#dictionary to store start time
start_stamp = {}

# Function to delete a pair
async def delete_pair(id_to_delete):
    global chat_pairs
    for pair in chat_pairs:
        if id_to_delete in pair:
            user1, user2 = pair
            start_time1 = start_stamp.get(f"user_{user1}")
            start_time2 = start_stamp.get(f"user_{user2}")
            start_set_time1 = datetime.strptime(start_time1, "%Y-%m-%d %H:%M:%S")
            start_set_time2 = datetime.strptime(start_time2, "%Y-%m-%d %H:%M:%S")
            msg_time1 = message_timestamps.get(f"user_{user1}")
            msg_time2 = message_timestamps.get(f"user_{user2}")
            last_message_time1 = datetime.strptime(msg_time1, "%Y-%m-%d %H:%M:%S")
            last_message_time2 = datetime.strptime(msg_time2, "%Y-%m-%d %H:%M:%S")
            old_chat_time1 = vip_users_details(user1, "chat_time") if vip_users_details(user1, "chat_time") is not None else 0
            old_chat_time2 = vip_users_details(user2, "chat_time") if vip_users_details(user2, "chat_time") is not None else 0
            upate_chat_time1 = ((last_message_time1 - start_set_time1).seconds + old_chat_time1)
            upate_chat_time2 = ((last_message_time2 - start_set_time2).seconds + old_chat_time2)
            print(upate_chat_time1, upate_chat_time2)
            save_premium_user(user1, chat_time = upate_chat_time1)
            save_premium_user(user2, chat_time = upate_chat_time2)
            print(vip_users_details(user2, "chat_time"), vip_users_details(user2, "chat_time"), "final" )
    for i, pair in enumerate(chat_pairs):
        if id_to_delete in pair:
            del chat_pairs[i]
            return True
    return False

# Function to add a pair
def add_pair(new_pair):
    global chat_pairs
    chat_pairs.append(new_pair)


button_pattern = re.compile(r"^(🔍 (Search for an interlocutor|Найти собеседника|Məqalə axtar) 🔎)$")

@cbot.on_message(filters.private & filters.regex(button_pattern) & subscribed & user_registered)
async def search_interlocutor(client, message):
    user_language = find_language(message.from_user.id)  # Retrieve user's language
    # Create keyboard with start searching button
    keyboard = ReplyKeyboardMarkup(([
    [KeyboardButton(await translate_async("Normal Search", user_language))], 
    [KeyboardButton(await translate_async("Configured Search", user_language))],
    [KeyboardButton(await translate_async("Find a Guy", user_language))],
    [KeyboardButton(await translate_async("Find a Girl", user_language))]]),
    resize_keyboard=True)
    caption = await translate_async(f"Your language:{user_language}\nChoose the button below to find an interlocutor.", user_language)
    await message.reply(caption, reply_markup=keyboard)


#Normal search
@cbot.on_message(filters.private & filters.regex("Normal Search|Обычный поиск|Normal axtarış") & subscribed & user_registered)
async def normal_search(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    try:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                await message.reply(await translate_async("You are already in a chat.", language))
                return
        # Check if user is already searching
        for user in searching_users:
            if user["user_id"] == user_id:
                await message.reply("You are already searching.")
                return
        # Get normal user's details
        gender = get_gender(user_id, "huls")
        age_groups = get_age_group(user_id, "huls")
        interest = get_interest(user_id, "huls")
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for an interlocutor...", language), reply_markup=keyboard)
        chk = await apppend_id(user_id, language, gender, age_groups, interest)
        if chk:
            await match_genral()
        else:
            await message.reply(await translate_async("failed to search.", language), reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Error: {e}")

# Handle stop search button
@cbot.on_message(filters.private & filters.regex("Stop Searching|Прекратить поиск|Axtarışı dayandırın") & subscribed & user_registered)
async def stop_search(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    # Remove user from searching list
    for i, user in enumerate(searching_users):
        if user["user_id"] == user_id:
            del searching_users[i]
            break
    for i, user in enumerate(searching_premium_users):
        if user["user_id"] == user_id:
            del searching_premium_users[i]
            break
    reply_markup = await get_reply_markup(language)
    await message.reply(await translate_async("Search stopped.", language), reply_markup=reply_markup)


async def apppend_id(user_id, language, gender, age_groups, interest):
    await asyncio.sleep(2)
    searching_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": interest})
    return True

# Function to match users and start chatting
async def match_genral():
    count = 2
    matched = False
    while count < 1:
        print("function called")
        for i, user1 in enumerate(searching_users.copy()):
            for j, user2 in enumerate(searching_users[i+1:].copy(), i+1):
                if user1["language"] == user2["language"]:
                    # Match found, add pair to chat_pairs and notify users
                    new_pair = (user1["user_id"], user2["user_id"])
                    lang1 = find_language(user1["user_id"])
                    lang2 = find_language(user2["user_id"])
                    start_stamp[f"user_{user2["user_id"]}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    start_stamp[f"user_{user1["user_id"]}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    message_timestamps[f"user_{user2["user_id"]}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    message_timestamps[f"user_{user1["user_id"]}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    motel = vip_users_details(user1, "total_dialog")
                    motel2 = vip_users_details(user2, "total_dialog")
                    if motel:
                        total = motel
                    else:
                        total = 0
                    if motel2:
                        total2 = motel2
                    else:
                        total2 = 0                            
                    save_premium_user(user1, total_dialog= total + 1)
                    save_premium_user(user2, total_dialog= total2 + 1)
                    add_pair(new_pair)
                    # Remove users from searching lists
                    searching_users.remove(user1)
                    searching_users.remove(user2)
                    caption, markup = await interlocutor_normal_message(lang2)
                    caption1, markup1 = await interlocutor_normal_message(lang1)
                    await cbot.send_message(user1["user_id"], caption1, reply_markup=markup1)
                    await cbot.send_message(user2["user_id"], caption, reply_markup=markup)
                    matched = True  # Set flag to True
                    break  # Break out of inner loop if match found
            if matched:  # Break out of outer loop if match found
                break
    if not matched:
        count += 1

# Handle cancel button
@cbot.on_message(filters.private & filters.regex("End chat|Söhbəti bitirin|Конец чат|Söhbəti sonlandır|Завершить чат") & subscribed & user_registered)
async def cancel(_, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    # Find the other user in the pair and inform them
    for pair in chat_pairs:
        if user_id in pair:
            other_user_id = pair[1] if pair[0] == user_id else pair[0]
            other_user_lang = find_language(other_user_id)
            reply_markup2 = await get_reply_markup(other_user_lang)
            caption = await translate_async("Chat has been Ended by the other user.", other_user_lang)
            await cbot.send_message(other_user_id, caption, reply_markup=reply_markup2)
            break
        reply_markup = await get_reply_markup(language)
        await message.reply(await translate_async("Chat Ended.", language), reply_markup=reply_markup)
    # Find the chat pair and delete it
    if await delete_pair(user_id):
        pass


# Handle incoming messages
@cbot.on_message(filters.private & subscribed & user_registered)
async def forward_message(client, message):
    for pair in chat_pairs:
        if message.from_user.id in pair:
            user1, user2 = pair
            lang1 = find_language(user1)
            lang2 = find_language(user2)
            if message.from_user.id == user1:
                is_premium, _ = is_user_premium(user1)
                message_timestamps[f"user_{user1}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                if is_premium:
                    await cbot.copy_message(user2, message.chat.id, message.id)
                else: 
                    if message.text:
                        await cbot.copy_message(user2, message.chat.id, message.id)
                    else:
                        await cbot.send_message(user1, await translate_async("Sorry, you need to be a premium user to send photos, videos, stickers, and documents. Purchase premium for full access.", lang1))
            elif message.from_user.id == user2:
                is_premium, _ = is_user_premium(user2)
                message_timestamps[f"user_{user2}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                if is_premium:
                    await cbot.copy_message(user1, message.chat.id, message.id)
                else:
                    if message.text:
                        await cbot.copy_message(user1, message.chat.id, message.id)
                    else:
                        await cbot.send_message(user2, await translate_async("Sorry, you need to be a premium user to send photos, videos, stickers, and documents. Purchase premium for full access.", lang2))
            break


# function to check for inactive chats
async def check_inactive_chats():
    for pair in chat_pairs:
        if not pair:
            return
        user1, user2 = pair
        msg_time1 = message_timestamps.get(f"user_{user1}")
        msg_time2 = message_timestamps.get(f"user_{user2}")
        last_message_time1 = datetime.strptime(msg_time1, "%Y-%m-%d %H:%M:%S")
        last_message_time2 = datetime.strptime(msg_time2, "%Y-%m-%d %H:%M:%S")
        cr_time = datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "%Y-%m-%d %H:%M:%S")
        if last_message_time1 and last_message_time2:
            print((cr_time - last_message_time1).seconds)
            if (cr_time - last_message_time1).seconds > 60 and (cr_time - last_message_time2).seconds > 60:
                # Chat has been inactive for more than 10 minutes, end the chat
                await delete_pair(user1)
                lang1 = find_language(user1)
                lang2 = find_language(user2)
                reply_markup1 = await get_reply_markup(lang1)
                reply_markup2 = await get_reply_markup(lang2)
                caption1 = await translate_async("Chat has been ended due to inactivity.", lang1)
                caption2 = await translate_async("Chat has been ended due to inactivity.", lang2)
                await cbot.send_message(user1, caption1, reply_markup=reply_markup1)
                await cbot.send_message(user2, caption2, reply_markup=reply_markup2)



# function to check for inactive chats
async def check_inactive_chats():
    for pair in chat_pairs:
        if not pair:
            return
        user1, user2 = pair
        msg_time1 = message_timestamps.get(f"user_{user1}")
        msg_time2 = message_timestamps.get(f"user_{user2}")
        last_message_time1 = datetime.strptime(msg_time1, "%Y-%m-%d %H:%M:%S")
        last_message_time2 = datetime.strptime(msg_time2, "%Y-%m-%d %H:%M:%S")
        cr_time = datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "%Y-%m-%d %H:%M:%S")
        if last_message_time1 and last_message_time2:
            print((cr_time - last_message_time1).seconds)
            if (cr_time - last_message_time1).seconds > 60 and (cr_time - last_message_time2).seconds > 60:
                # Chat has been inactive for more than 10 minutes, end the chat
                await delete_pair(user1)
                lang1 = find_language(user1)
                lang2 = find_language(user2)
                reply_markup1 = await get_reply_markup(lang1)
                reply_markup2 = await get_reply_markup(lang2)
                caption1 = await translate_async("Chat has been ended due to inactivity.", lang1)
                caption2 = await translate_async("Chat has been ended due to inactivity.", lang2)
                await cbot.send_message(user1, caption1, reply_markup=reply_markup1)
                await cbot.send_message(user2, caption2, reply_markup=reply_markup2)

# Schedule the task to run every 10 minutes
scheduler.add_job(check_inactive_chats, 'interval', minutes=1)

# Start the scheduler
scheduler.start()