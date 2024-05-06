#await match_users(gender="male", age_groups=["18-24"], language="english")

import asyncio
from datetime import datetime
import time
import re
import apscheduler.schedulers.asyncio as aps
from pyrogram import filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from helpers.forcesub import subscribed, user_registered
from helpers.helper import find_language, get_age_group, get_gender, get_interest
from helpers.translator import translate_async
from langdb.get_msg import get_reply_markup, interlocutor_normal_message, interlocutor_vip_message
from Modules import cbot
from Modules.modules.register import get_user_name
from Modules.modules.configure import get_age_groups_text
from database.premiumdb import save_premium_user, vip_users_details, is_user_premium
from database.chatdb import save_user


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


@cbot.on_message(filters.command("hlo") & filters.private & subscribed & user_registered)
async def send_lists(client, message):
    lists = f"Normal users searching: {searching_users.copy()}\n\nPremium Users searching{searching_premium_users.copy()}\n{chat_pairs.copy()}"
    await message.reply(lists)


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
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton(await translate_async("Normal Search", user_language)), 
        KeyboardButton(await translate_async("Configured Search", user_language))],
        [KeyboardButton(await translate_async("Find a Guy", user_language)),
        KeyboardButton(await translate_async("Find a Girl", user_language))]],
        resize_keyboard=True)
    caption = await translate_async(f"Your language:{user_language}\nChoose the button below to find an interlocutor.", user_language)
    await message.reply(caption, reply_markup=keyboard)
    save_user(message.from_user.id)

@cbot.on_message(filters.private & filters.regex("Configured Search|Настроенный поиск|Konfiqurasiya edilmiş Axtarış") & subscribed & user_registered)
async def configured_search(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    prem_stat, _ = is_user_premium(user_id)
    if not prem_stat:
        await message.reply(await translate_async("Purchase premium first!", language))
        return
    try:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                await message.reply(await translate_async("You are already in a chat.", language))
                return
        # Check if user is already searching
        if await is_user_searching(user_id):
            await message.reply("You are already searching.")
            return
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for a interlocutor based on your configuration...", language), reply_markup=keyboard)
        gender = vip_users_details(message.from_user.id, "gender")
        age_groups = vip_users_details(message.from_user.id, "age_groups")
        room = vip_users_details(message.from_user.id, "room")
            # Send the current configuration message
        await message.reply(await translate_async(f"""Searching for a interlocutor based on your configuration...


--Current Configuration--:
                                                  
Gender: {gender if gender else "Any"} 
Age Group(s): \n{await get_age_groups_text(message.from_user.id, language)}  
Room: {room if room else "Any"} """, language))
        searching_premium_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": room})
        try:
            await match_users()
        except Exception as e:
            await message.reply(await translate_async(f"failed to search:{e}", language), reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Error: {e}")


#premium search for finding a female user
@cbot.on_message(filters.private & filters.regex("Find a Girl|Найди себе девушку|Bir qız tapın") & subscribed & user_registered)
async def normal_search(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    prem_stat, _ = is_user_premium(user_id)
    print(prem_stat)
    if not prem_stat:
        await message.reply(await translate_async("Purchase premium first!", language))
        return
    try:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                await message.reply(await translate_async("You are already in a chat.", language))
                return
        # Check if user is already searching
        if await is_user_searching(user_id):
            await message.reply("You are already searching.")
            return
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for a Female interlocutor...", language), reply_markup=keyboard)
        searching_premium_users.append({"user_id": user_id, "language": language, "gender": "female", "age_groups": None, "room": None})
        print("chking")
        try:
            await match_users()
        except Exception as e:
            await message.reply(await translate_async(f"failed to search:{e}", language), reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Error: {e}")


#premium search for finding a male user
@cbot.on_message(filters.private & filters.regex("Find a Guy|Найди парня|Bir Oğlan tapın") & subscribed & user_registered)
async def normal_search(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    prem_stat, _ = is_user_premium(user_id)
    if not prem_stat:
        await message.reply(await translate_async("Purchase premium first!", language))
        return
    try:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                await message.reply(await translate_async("You are already in a chat.", language))
                return
        # Check if user is already searching
        if await is_user_searching(user_id):
            await message.reply("You are already searching.")
            return
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for a Male interlocutor...", language), reply_markup=keyboard)
        searching_premium_users.append({"user_id": user_id, "language": language, "gender": "male", "age_groups": None, "room": None})
        print("chking")
        try:
            await match_users()
        except Exception as e:
            await message.reply(await translate_async(f"failed to search:{e}", language), reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Error: {e}")

#Normal search
@cbot.on_message(filters.private & filters.regex("Normal Search|Обычный поиск|Normal Axtarış") & subscribed & user_registered)
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
        if await is_user_searching(user_id):
            await message.reply("You are already searching.")
            return
        # Get normal user's details
        gender = get_gender(user_id, "huls")
        age_groups = get_age_group(user_id, "huls")
        interest = get_interest(user_id, "huls").lower()
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for an interlocutor...", language), reply_markup=keyboard)
        chk = await apppend_id(user_id, language, gender, age_groups, interest)
        print("chking")
        if chk:
            await match_users()
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

async def match_users():
    count = 0
    while count < 1:
        print("function called")
        matched = False
        # Match premium users with normal users
        for premium_user in searching_premium_users.copy():
            print(f"Processing premium user {premium_user['user_id']}...")
            for normal_user in searching_users.copy():
                print(f"Processing normal user {normal_user['user_id']}...")
                if (premium_user["language"] == normal_user["language"] and
                    (premium_user["gender"] == normal_user["gender"] or premium_user["gender"] == "any gender" or premium_user["gender"] is None) and
                    (premium_user["age_groups"] is None or normal_user["age_groups"] in premium_user["age_groups"] if premium_user["age_groups"] is not None else True) and
                    (premium_user["room"] == normal_user["room"] or premium_user["room"] == "any" or premium_user["room"] is None)):
                    print(f"Match found between premium user {premium_user['user_id']} and normal user {normal_user['user_id']}.")
                    await process_match(premium_user, normal_user)
                    matched = True
            if matched:
                print(f"Match found for premium user {premium_user['user_id']}. Exiting loop...")
                break
        if not matched:
            # Match normal users with other normal users
            for i, user1 in enumerate(searching_users.copy()):
                print(f"Processing normal user {user1['user_id']}...")
                for j, user2 in enumerate(searching_users[i+1:].copy(), i+1):
                    print(f"Processing normal user {user2['user_id']}...")
                    if user1["language"] == user2["language"]:
                        print(f"Match found between normal user {user1['user_id']} and normal user {user2['user_id']}.")
                        await process_match(user1, user2)
                        matched = True
                        break
                if matched:
                    print(f"Match found for normal user {user1['user_id']}. Exiting loop...")
                    break

        if not matched:
            count += 1
            print(f"No matches found after {count} iterations. Exiting loop...")

async def is_user_searching(user_id):
    for user in searching_users:
        if user["user_id"] == user_id:
            return True
    for user in searching_premium_users:
        if user["user_id"] == user_id:
            return True
    return False


# def is_match(user1, user2):
#     return (user1["language"] == user2["language"] and
#             (user1["gender"] == user2["gender"] or user1["gender"] == "any gender" or user1["gender"] is None) and
#             (user1["age_groups"] is None or user2["age_groups"] in user1["age_groups"] if user1["age_groups"] is not None else True) and
#             (user1["room"] == user2["room"] or user1["room"] == "any" or user1["room"] is None))


async def process_match(user1, user2):
    new_pair = (user1["user_id"], user2["user_id"])
    add_pair(new_pair)
    
    # Remove user from searching list
    for i, user in enumerate(searching_users):
        if user["user_id"] == user1["user_id"]:
            del searching_users[i]
            break  # Exit the loop once user is found and removed
    else:
        for i, vip_user in enumerate(searching_premium_users):
            if vip_user["user_id"] == user1["user_id"]:
                del searching_premium_users[i]
                break  # Exit the loop once user is found and removed

    for i, user in enumerate(searching_users):
        if user["user_id"] == user2["user_id"]:
            del searching_users[i]
            break  # Exit the loop once user is found and removed
    else:
        for i, vip_user in enumerate(searching_premium_users):
            if vip_user["user_id"] == user2["user_id"]:
                del searching_premium_users[i]
                break  # Exit the loop once user is found and removed

    await update_user_dialogs(user1, user2)
    await send_match_messages(user1, user2)


async def update_user_dialogs(user1, user2):
    motel1 = vip_users_details(user1["user_id"], "total_dialog")
    motel2 = vip_users_details(user2["user_id"], "total_dialog")
    total1 = motel1 if motel1 else 0
    total2 = motel2 if motel2 else 0
    save_premium_user(user1["user_id"], total_dialog=total1 + 1)
    save_premium_user(user2["user_id"], total_dialog=total2 + 1)
    start_stamp[f"user_{user1['user_id']}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    start_stamp[f"user_{user2['user_id']}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    message_timestamps[f"user_{user1['user_id']}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    message_timestamps[f"user_{user2['user_id']}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

async def send_match_messages(user1, user2):
    lang1 = find_language(user1["user_id"])
    lang2 = find_language(user2["user_id"])
    is_vip1, _ = is_user_premium(user1["user_id"])
    is_vip2, _ = is_user_premium(user2["user_id"])
    name = await get_user_name(user2["user_id"])
    keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", lang1))]], resize_keyboard=True, one_time_keyboard=True)
    if is_vip1:
        cap1 = await interlocutor_vip_message(lang1, name, user2["gender"], user2["age_groups"])
    else:
        cap1 = await interlocutor_normal_message(lang1)
    await cbot.send_message(user1["user_id"], cap1, reply_markup=keyboard)
    if is_vip2:
        caption = await interlocutor_vip_message(lang2, name, user1["gender"], user1["age_groups"])
    else:
        caption = await interlocutor_normal_message(lang2)
    await cbot.send_message(user2["user_id"], caption, reply_markup=keyboard)


# Handle cancel button
@cbot.on_message(filters.private & filters.regex("End chat|Söhbəti bitirin|Конец чат|Söhbəti sonlandır|Завершить чат") & subscribed & user_registered)
async def end_chat(_, message):
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
            reply_markup = await get_reply_markup(language)
            await message.reply(await translate_async("Chat Ended.", language), reply_markup=reply_markup)
    # Find the chat pair and delete it
    await delete_pair(user_id)
    await message.reply(await translate_async("Can you leave a review about your interlocutor?", language), reply_markup= await get_rating_markup(other_user_id))
    await cbot.send_message(other_user_id, await translate_async("How would you rate this chat?", language), reply_markup= await get_rating_markup(user_id))


async def get_rating_markup(user_id):
    lang = find_language(user_id) 
    # Buttons for rating emojis
    buttons = [
        [
            InlineKeyboardButton(await translate_async("👍 Good", lang), callback_data=f"emoji_👍_{user_id}"),
            InlineKeyboardButton(await translate_async("👎 Bad", lang), callback_data=f"emoji_👎_{user_id}")
        ],
        [
            InlineKeyboardButton(await translate_async("⛔ Fraudster/Scam/Advertising", lang), callback_data=f"emoji_⛔_{user_id}")
        ],
        [
            InlineKeyboardButton(await translate_async("Skip for now!", lang), callback_data=f"skip_handle")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    return reply_markup

# Handle the rating response
@cbot.on_callback_query(filters.regex(r"emoji_.*") & subscribed & user_registered)
async def handle_rating(_, query):
    user_id = query.from_user.id
    language = find_language(user_id)
    rating_emoji = query.data.split("_")[1]
    other_user_id = query.data.split("_")[2]
    rating = {str(rating_emoji): 1}
    print(rating, other_user_id)
    save_user(other_user_id, rating=rating)
    await query.message.edit_text(await translate_async("Thank you for your feedback!", language))

@cbot.on_callback_query(filters.regex(r"skip_handle") & subscribed & user_registered)
async def handle_skip(_, query):
    try:
        # Delete the callback message
        await query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)


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


# Schedule the task to run every 10 minutes
scheduler.add_job(check_inactive_chats, 'interval', minutes=1)

# Start the scheduler
scheduler.start()
