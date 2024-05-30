import os
import asyncio
from datetime import datetime
import time
import re
import pyrostep
from collections import deque
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Message, CallbackQuery

# Helpers
from helpers.filters import subscribed, user_registered
from helpers.helper import find_language, get_age_group, get_gender, get_interest
from helpers.translator import translate_async
from helpers.fren_req import process_friend_request

# Language Database
from langdb.get_msg import get_reply_markup, interlocutor_normal_message, interlocutor_vip_message

# Modules
from Modules import cbot, scheduler, ADMIN_IDS, REPORT_CHAT
from Modules.modules.register import get_user_name
from Modules.modules.advertisement import advert_user
from Modules.modules.configure import get_age_groups_text
from Modules.modules.shear import check_shear_url

# Database
from database.premiumdb import save_premium_user, vip_users_details, is_user_premium
from database.chatdb import save_user
from database.residuedb import add_bluser, unblock_user


pyrostep.listen(cbot)

# List to store users searching for an interlocutor
searching_users = []
searching_premium_users = []

# List to store pairs of users for chatting
chat_pairs = []


#List to store premium users searching mode for next search
prem_searching_mode = []

#Lisr to store normal users searching mode for next search
normal_searching_mode = []

# Dictionary to store last message timestamps for each user
message_timestamps = {}

#dictionary to store the messages for each user
messages = {}

#dictionary to store start time
start_stamp = {}

# Track profanity; ban after 3 offenses in a single chat
profanity_scores = {}


@cbot.on_message(filters.command("hlo") & filters.user(ADMIN_IDS) & filters.private & subscribed & user_registered)
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
            save_premium_user(user1, chat_time = upate_chat_time1)
            save_premium_user(user2, chat_time = upate_chat_time2)
            old_chat_time3 = vip_users_details(user1, "weekly_chat_time") if vip_users_details(user1, "weekly_chat_time") is not None else 0
            old_chat_time4 = vip_users_details(user2, "weekly_chat_time") if vip_users_details(user2, "weekly_chat_time") is not None else 0
            upate_chat_time3 = ((last_message_time1 - start_set_time1).seconds + old_chat_time3)
            upate_chat_time4 = ((last_message_time2 - start_set_time2).seconds + old_chat_time4)
            save_premium_user(user1, weekly_chat_time = upate_chat_time3)
            save_premium_user(user2, weekly_chat_time = upate_chat_time4)
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
    await advert_user(message.from_user.id, user_language)
    # Create keyboard with start searching button
    keyboard = ReplyKeyboardMarkup([
        [
            KeyboardButton(await translate_async("Normal Search", user_language))
        ],
        [
            KeyboardButton(await translate_async("Find a Guy", user_language)),
            KeyboardButton(await translate_async("Find a Girl", user_language))
        ],
        [
            KeyboardButton(await translate_async("Configured Search", user_language)),
            KeyboardButton(await translate_async("Back", user_language))
        ]
    ],
        resize_keyboard=True)
    caption = await translate_async(f"Your language:{user_language}\nChoose the button below to find an interlocutor.", user_language)
    await message.reply(caption, reply_markup=keyboard)
    save_user(message.from_user.id)

@cbot.on_message(filters.private & filters.regex("Configured Search|Настроенный поиск|Konfiqurasiya edilmiş Axtarış") & subscribed & user_registered)
async def configured_search(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    prem_stat, _ = is_user_premium(user_id)
    await advert_user(user_id, language)
    if not prem_stat:
        await message.reply(await translate_async("Purchase premium first!", language))
        return
    try:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", language))]], resize_keyboard=True, one_time_keyboard=True)
                await message.reply(await translate_async("You are already in a chat. End the chat first by using below button!", language), reply_markup = keyboard)
                return
        # Check if user is already searching
        if is_user_searching(user_id):
            keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
            await message.reply("You are already searching. Stop searching first by using below button!", reply_markup = keyboard)
            return
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for a interlocutor based on your configuration...", language), reply_markup=keyboard)
        gender = vip_users_details(message.from_user.id, "gender")
        age_groups = vip_users_details(message.from_user.id, "age_groups")
        room = vip_users_details(message.from_user.id, "room").split(",")
            # Send the current configuration message
        await message.reply(await translate_async(f"""Searching for a interlocutor based on your configuration...


--Current Configuration--:
                                                  
Gender: {gender if gender else "Any"} 
Age Group(s): \n{await get_age_groups_text(message.from_user.id, language)}  
Room: {room if room else "Any"} """, language))
        searching_premium_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": room})
        user_index = next((i for i, d in enumerate(prem_searching_mode) if d["user_id"] == user_id), None)
        if user_index is not None:
            prem_searching_mode.insert(user_index, {"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": room})
        else:
            prem_searching_mode.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": room})
        try:
            await match_users()
            await asyncio.sleep(40)
            # Check if user is still searching
            for premium_user in searching_premium_users.copy():
                if premium_user["user_id"] == user_id:
                    await remove_user_from_searching_lists(user_id)
                    await message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))
            for normal_user in searching_users.copy():
                if normal_user["user_id"] == user_id:
                    await remove_user_from_searching_lists(user_id)
                    await message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))
        except Exception as e:
            await message.reply(await translate_async(f"failed to search:{e}", language), reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Error: {e}")


#premium search for finding a female user
@cbot.on_message(filters.private & filters.regex("Find a Girl|Найди себе девушку|Bir qız tapın") & subscribed & user_registered)
async def normal_search(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    await advert_user(user_id, language)
    prem_stat, _ = is_user_premium(user_id)
    if not prem_stat:
        await message.reply(await translate_async("Purchase premium first!", language))
        return
    try:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", language))]], resize_keyboard=True, one_time_keyboard=True)
                await message.reply(await translate_async("You are already in a chat. End the chat first by using below button!", language), reply_markup = keyboard)
                return
        # Check if user is already searching
        if is_user_searching(user_id):
            keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
            await message.reply("You are already searching. Stop searching first by using below button!", reply_markup = keyboard)
            return
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for a Female interlocutor...", language), reply_markup=keyboard)
        searching_premium_users.append({"user_id": user_id, "language": language, "gender": "female", "age_groups": None, "room": None})
        user_index = next((i for i, d in enumerate(prem_searching_mode) if d["user_id"] == user_id), None)
        if user_index is not None:
            prem_searching_mode.insert(user_index, {"user_id": user_id, "language": language, "gender": "female", "age_groups": None, "room": None})
        else:
            prem_searching_mode.append({"user_id": user_id, "language": language, "gender": "female", "age_groups": None, "room": None})
        try:
            await match_users()
            await asyncio.sleep(40)
            # Check if user is still searching
            for premium_user in searching_premium_users.copy():
                if premium_user["user_id"] == user_id:
                    await remove_user_from_searching_lists(user_id)
                    await message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))
            for normal_user in searching_users.copy():
                if normal_user["user_id"] == user_id:
                    await remove_user_from_searching_lists(user_id)
                    await message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))
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
    await advert_user(user_id, language, bool(prem_stat))
    if not prem_stat:
        await message.reply(await translate_async("Purchase premium first!", language))
        return
    try:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", language))]], resize_keyboard=True, one_time_keyboard=True)
                await message.reply(await translate_async("You are already in a chat. End the chat first by using below button!", language), reply_markup = keyboard)
                return
        # Check if user is already searching
        if is_user_searching(user_id):
            keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
            await message.reply("You are already searching. Stop searching first by using below button!", reply_markup = keyboard)
            return
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for a Male interlocutor...", language), reply_markup=keyboard)
        searching_premium_users.append({"user_id": user_id, "language": language, "gender": "male", "age_groups": None, "room": None})
        user_index = next((i for i, d in enumerate(prem_searching_mode) if d["user_id"] == user_id), None)
        if user_index is not None:
            prem_searching_mode.insert(user_index, {"user_id": user_id, "language": language, "gender": "male", "age_groups": None, "room": None})
        else:
            prem_searching_mode.append({"user_id": user_id, "language": language, "gender": "male", "age_groups": None, "room": None})
        try:
            await match_users()
            await asyncio.sleep(40)
            # Check if user is still searching
            for premium_user in searching_premium_users.copy():
                if premium_user["user_id"] == user_id:
                    await remove_user_from_searching_lists(user_id)
                    await message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))
            for normal_user in searching_users.copy():
                if normal_user["user_id"] == user_id:
                    await remove_user_from_searching_lists(user_id)
                    await message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))

        except Exception as e:
            await message.reply(await translate_async(f"failed to search:{e}", language), reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Error: {e}")

def is_chatting(user_id, message, language):
    # Check if user is already in a chat
    for pair in chat_pairs:
        if user_id in pair:
            return True
            break
    return False
            
#Normal search
@cbot.on_message(filters.private & filters.regex("Normal Search|Обычный поиск|Normal Axtarış") & subscribed & user_registered)
async def normal_search(client, message: Message):
    user_id = message.from_user.id
    language = find_language(user_id)
    await advert_user(user_id, language)
    try:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", language))]], resize_keyboard=True, one_time_keyboard=True)
                await message.reply(await translate_async("You are already in a chat. End the chat first by using below button!", language), reply_markup = keyboard)
                return
        # Check if user is already searching
        if is_user_searching(user_id):
            keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
            await message.reply("You are already searching. Stop searching first by using below button!", reply_markup = keyboard)
            return
        # Get normal user's details
        gender = get_gender(user_id, "huls")
        age_groups = get_age_group(user_id, "huls")
        interest = get_interest(user_id, "huls").lower().split(" ")
        language = find_language(user_id)
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for an interlocutor...", language), reply_markup=keyboard)
        chk = await append_id(user_id, language, gender, age_groups, interest)
        if chk:
            await match_users()
            await asyncio.sleep(40)
            # Check if user is still searching
            for premium_user in searching_premium_users.copy():
                if premium_user["user_id"] == user_id:
                    await remove_user_from_searching_lists(user_id)
                    await message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))
            for normal_user in searching_users.copy():
                if normal_user["user_id"] == user_id:
                    await remove_user_from_searching_lists(user_id)
                    await message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))
        else:
            await message.reply(await translate_async("failed to search.", language), reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Error: {e}")

# Handle stop search button
@cbot.on_message(filters.private & filters.regex("Stop Searching|Прекратить поиск|Axtarışı dayandırın") & subscribed & user_registered)
async def stop_search(_, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    
    # Part 1: Remove user from searching lists
    await remove_user_from_searching_lists(user_id)

    # Part 2: Send reply to user
    reply_markup = await get_reply_markup(language)
    await message.reply(await translate_async("Search stopped.", language), reply_markup=reply_markup)
    await advert_user(user_id, language)


async def remove_user_from_searching_lists(user_id):
    for i, user in enumerate(searching_users):
        if user["user_id"] == user_id:
            del searching_users[i]
            break
    for i, user in enumerate(searching_premium_users):
        if user["user_id"] == user_id:
            del searching_premium_users[i]
            break
    return


async def append_id(user_id, language, gender, age_groups, interest):
    await asyncio.sleep(2)
    searching_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": interest})
    # Append the normal user id into normal_searching_mode list
    user_index = next((i for i, d in enumerate(normal_searching_mode) if d["user_id"] == user_id), None)
    if user_index is not None:
        normal_searching_mode.insert(user_index, {"user_id": user_id, "language": language, "gender": "male", "age_groups": age_groups, "room": interest})
    else:
        normal_searching_mode.append({"user_id": user_id, "language": language, "gender": "male", "age_groups": age_groups, "room": interest})
    return True

async def match_users():
    count = 0
    while count < 1:
        matched = False
        # Match premium users with normal users
        for premium_user in searching_premium_users.copy():
            for normal_user in searching_users.copy():
                if (premium_user["language"] == normal_user["language"] and
                    (premium_user["gender"] == normal_user["gender"] or premium_user["gender"] == "any gender" or premium_user["gender"] is None) and
                    (premium_user["age_groups"] is None or normal_user["age_groups"] in premium_user["age_groups"] if premium_user["age_groups"] is not None else True)): # and
                    # any(interest in premium_user["room"] for interest in normal_user["room"]) or premium_user["room"] == ["any"] or premium_user["room"] is None):
                    await process_match(premium_user, normal_user)
                    matched = True
            if matched:
                break
        if not matched:
            for i , prem1 in enumerate(searching_premium_users.copy()):
                for j, prem2 in enumerate(searching_premium_users[i+1:].copy(), i+1):
                    # print(f"premium match = ij= {i, j} prem1 = {int(prem1["user_id"])} prem2 = {int(prem2["user_id"])}")
                    # Getting users details
                    user1 = int(prem1["user_id"])
                    lang1 = find_language(user1)
                    gen1 = get_gender(user1, "_")
                    age1 = get_age_group(user1, "_")
                    room1 = prem1["room"] 

                    user2 = int(prem2["user_id"])
                    lang2 = find_language(user2)
                    gen2 = get_gender(user2, "_")
                    age2 = get_age_group(user2, "_")
                    room2 = prem2["room"] 

                    # Match premium users with other premium user
                    if (lang1 == lang2 and
                        (prem1["gender"] == gen2 or prem1["gender"] == "any gender" or prem1["gender"] is None) and
                        (prem2["gender"] == gen1 or prem2["gender"] == "any gender" or prem2["gender"] is None) and
                        (prem1["age_groups"] is None or age1 in prem2["age_groups"] if prem1["age_groups"] is not None else True) and
                        (prem2["age_groups"] is None or age2 in prem1["age_groups"] if prem2["age_groups"] is not None else True) and
                        any(interest in room1 for interest in room2) or room1 == ["any"] or room1 is None or room2 == ["any"] or room2 is None):
                        await process_match(prem1, prem2)
                        matched = True
                if matched:
                    break
        if not matched:
            # Match normal users with other normal users
            for i, user1 in enumerate(searching_users.copy()):
                for j, user2 in enumerate(searching_users[i+1:].copy(), i+1):
                    if user1["language"] == user2["language"]:
                        await process_match(user1, user2)
                        matched = True
                        break
                if matched:
                    break
        if not matched:
            count += 1

def is_user_searching(user_id):
    for user in searching_users.copy():
        if user["user_id"] == user_id:
            return True
    for user in searching_premium_users.copy():
        if user["user_id"] == user_id:
            return True
    return False


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
    name1 = await get_user_name(user1["user_id"])
    name2 = await get_user_name(user2["user_id"])
    verify_status1 = vip_users_details(user1["user_id"], "verified") if vip_users_details(user1["user_id"], "verified") else "False"
    verify_status2 = vip_users_details(user2["user_id"], "verified") if vip_users_details(user2["user_id"], "verified") else "False"
    keyboard = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton(await translate_async("End chat", lang1)),
                KeyboardButton(await translate_async("Add as Friend", lang1))
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    if is_vip1:
        cap1 = await interlocutor_vip_message(lang1, name2, get_gender(user2["user_id"], "_"),vip_users_details(user2["user_id"], "age"), verify_status2)
    else:
        cap1 = await interlocutor_normal_message(lang1, verify_status2)
    await cbot.send_message(user1["user_id"], cap1, reply_markup=keyboard)
    if is_vip2:
        caption = await interlocutor_vip_message(lang2, name1, get_gender(user1["user_id"], "_"), vip_users_details(user1["user_id"], "age"), verify_status1)
    else:
        caption = await interlocutor_normal_message(lang2, verify_status1)
    await cbot.send_message(user2["user_id"], caption, reply_markup=keyboard)

async def get_rating_markup(user_id):
    lang = find_language(user_id) 
    # Buttons for rating emojis
    buttons = [
        [
            InlineKeyboardButton(await translate_async("👍 Good", lang), callback_data=f"emoji_👍_{user_id}"),
            InlineKeyboardButton(await translate_async("🤡 Dumb", lang), callback_data=f"emoji_🤡_{user_id}"),
            InlineKeyboardButton(await translate_async("👎 Bad", lang), callback_data=f"emoji_👎_{user_id}")
        ],
        [
            InlineKeyboardButton(await translate_async("⛔ Fraudster/Scam/Advertising", lang), callback_data=f"emoji_⛔_{user_id}")
        ],
        [
            InlineKeyboardButton(await translate_async("Skip for now!", lang), callback_data=f"skip_handle"),
            InlineKeyboardButton(await translate_async("Next➡️", lang), callback_data="next_search")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    return reply_markup

#code for next search
@cbot.on_callback_query(filters.regex("next_search"))
async def next_search(_, query):
    user_id = query.from_user.id
    lang = find_language(user_id)
    # Check if user_id exists in premium searching mode list
    for user in prem_searching_mode:
        if user["user_id"] == user_id:
            language = user["language"]
            gender = user["gender"]
            age_groups = user["age_groups"]
            room = user["room"]
            mode = "premium"
            break
    else:
        # Check if user_id exists in normal searching mode list
        for user in normal_searching_mode:
            if user["user_id"] == user_id:
                language = user["language"]
                gender = user["gender"]
                age_groups = user["age_groups"]
                room = user["room"]
                mode = "normal"
                break
        else:
            # If user_id not found in either list, inform user to start a chat first
            await query.message.reply("Please start a chat first to use this feature.")
            return

    # If user_id found, proceed with next search
    if mode == "premium":
       searching_premium_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": room}) 
    elif mode == "normal":
        searching_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": room})
    await query.message.edit_text(await translate_async("Started searching for a interlocutor... ", lang))
    await match_users()
    await asyncio.sleep(40)
    for premium_user in searching_premium_users.copy():
        if premium_user["user_id"] == user_id:
            await remove_user_from_searching_lists(user_id)
            await query.message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))
    for normal_user in searching_users.copy():
        if normal_user["user_id"] == user_id:
            await remove_user_from_searching_lists(user_id)
            await query.message.reply(await translate_async("No interlocutor found! Please try again in different list", language), reply_markup = await get_reply_markup(language))

@cbot.on_message(filters.private & filters.regex("Add as Friend") & subscribed & user_registered)
async def add_as_friend(client, message: Message):
    user_id = message.from_user.id
    language = find_language(user_id)
    for pair in chat_pairs:
        if user_id in pair:
            friend_id = pair[1] if pair[0] == user_id else pair[0]
            break
    else:
        # reply that you are not in a chat
        await message.reply(text = await translate_async("You are not in a chat!!", language))
        return
    await process_friend_request(client, message, user_id, friend_id, language)

@cbot.on_message(filters.private & filters.regex("End chat|Söhbəti bitirin|Конец чат|Söhbəti sonlandır|Завершить чат") & subscribed & user_registered)
async def end_chat(_, message: Message):
    user_id = message.from_user.id
    language = find_language(user_id)
    await advert_user(user_id, language)
    # Find the other user in the pair and inform them
    for pair in chat_pairs:
        if user_id in pair:
            other_user_id = pair[1] if pair[0] == user_id else pair[0]
            await reset_profanity_scores(other_user_id)
            await reset_profanity_scores(user_id)
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


# Handle the rating response
@cbot.on_callback_query(filters.regex(r"emoji_.*") & subscribed & user_registered)
async def handle_rating(_, query):
    user_id = query.from_user.id
    language = find_language(user_id)
    rating_emoji = query.data.split("_")[1]
    other_user_id = query.data.split("_")[2]
    rating = {str(rating_emoji): 1}
    save_user(other_user_id, rating=rating)
    if rating_emoji == "⛔":
        # Ask for a report
        buttons = [
            [
                InlineKeyboardButton(await translate_async("Yes, report this user", language), callback_data=f"report_{other_user_id}"),
                InlineKeyboardButton(await translate_async("No, nevermind", language), callback_data=f"skip_handle")
            ]
        ]
        markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(await translate_async("Do you want to report this user?", language), reply_markup=markup)
    else:
        buttons = [
        [
            InlineKeyboardButton(await translate_async("Close❌", language), callback_data=f"skip_handle"),
            InlineKeyboardButton(await translate_async("Next➡️", language), callback_data="next_search")
        ]
    ]
        markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(await translate_async("Thank you for your feedback!", language), reply_markup = markup)

# Handle the report response
@cbot.on_callback_query(filters.regex(r"report_.*") & subscribed & user_registered)
async def handle_report(client, query):
    user_id = query.from_user.id
    language = find_language(user_id)
    other_user_id = int(query.data.split("_")[1])
    await query.message.edit_text(await translate_async("Please enter a message to report:", language))
    try:
        report_msg_obj = await pyrostep.wait_for(user_id, timeout= 90)
        report_msg = report_msg_obj.text
    except TimeoutError:
        await query.message.reply(await translate_async("No report message received, Reporting cancelled !!", language))
    global messages
    # Retrieve the messages for the other user
    messages_from = messages.get(other_user_id, [])

    if messages_from:
        # Send each message to the report_chat
        for message in messages_from:  
            try:
                await message.forward(REPORT_CHAT)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await message.forward(REPORT_CHAT)
    await client.send_message(REPORT_CHAT, f"#Report\n\n**Reported to**: {other_user_id}\n**Reported by**: {user_id}\n**Report Message**: {report_msg}\n\nAbove is his/her last 10 messages.")
    buttons = [
        [
            InlineKeyboardButton(await translate_async("Close❌", language), callback_data=f"skip_handle"),
            InlineKeyboardButton(await translate_async("Next➡️", language), callback_data="next_search")
        ]
    ]
    markup = InlineKeyboardMarkup(buttons)
    # Send a confirmation message to the user
    await query.message.edit_text(await translate_async("Thank you for your report. We have sent all messages from this user to the report chat for review.", language), reply_markup = markup)




@cbot.on_callback_query(filters.regex(r"skip_handle") & subscribed & user_registered)
async def handle_skip(_, query):
    try:
        # Delete the callback message
        await query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

# Handle incoming messages
@cbot.on_message(filters.private & subscribed & user_registered)
async def forward_message(client, message: Message):
    for pair in chat_pairs:
        if message.from_user.id in pair:
            user1, user2 = pair
            lang1 = find_language(user1)
            lang2 = find_language(user2)
            if message.from_user.id == user1:
                save_user(user1, total_message= 1)
                is_premium, _ = is_user_premium(user1)
                message_timestamps[f"user_{user1}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                if message.text or message.caption:
                    chk = await check_shear_url(user1, message, lang1)
                    if chk:
                        await check_profanity(user1, user2, message)
                        save_user(user1, profanity_score=1)
                        return
                if is_premium:
                    if not vip_users_details(user1, "block_media"):
                        await cbot.copy_message(user2, message.chat.id, message.id)
                    elif not message.text:
                        await cbot.send_message(user1, await translate_async("⚠️ Warning: You have been blocked to send media in chat. Please refrain from sending media. Thank you! 🚫", lang1))
                    else:
                        await cbot.copy_message(user2, message.chat.id, message.id)
                else: 
                    if message.text:
                        await cbot.copy_message(user2, message.chat.id, message.id)
                    else:
                        await cbot.send_message(user1, await translate_async("🔐 Access to sending photos, videos, stickers, and documents is exclusively for premium users. Upgrade to premium NOW for full access to all features! 💼💫", lang1))
                store_message(user1, message)
            elif message.from_user.id == user2:
                save_user(user2, total_message= 1)
                is_premium, _ = is_user_premium(user2)
                message_timestamps[f"user_{user2}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                if message.text or message.caption:
                    chk = await check_shear_url(user2, message, lang2)
                    if chk: 
                        await check_profanity(user2, user1, message)
                        save_user(user2, profanity_score=1)
                        return
                if is_premium:
                    if not vip_users_details(user2, "block_media"):
                        await cbot.copy_message(user1, message.chat.id, message.id)
                    elif not message.text:
                        await cbot.send_message(user2, await translate_async("⚠️ Warning: You have been blocked to send media in chat. Please refrain from sending media. Thank you! 🚫", lang2))
                    else:
                        await cbot.copy_message(user1, message.chat.id, message.id)
                else:
                    if message.text:
                        await cbot.copy_message(user1, message.chat.id, message.id)
                    else:
                        await cbot.send_message(user2, await translate_async("🔐 Access to sending photos, videos, stickers, and documents is exclusively for premium users. Upgrade to premium NOW for full access to all features! 💼💫", lang2))
                store_message(user2, message)           
            break

def store_message(user_id, message):
    """Store the user's message in a deque and add it to the messages dictionary."""
    if user_id not in messages:
        # Create a new deque for the user and add the message
        messages[user_id] = deque([message], maxlen=10)
    else:
        # Add the message to the existing deque for the user
        messages[user_id].append(message)

async def check_profanity(user1, user2, message: Message):
    if user1 in profanity_scores:
        profanity_scores[user1] += 1
    else:
        profanity_scores[user1] = 1
    if profanity_scores[user1] >= 3:
        lang1 = find_language(user1)
        lang2 = find_language(user2)
        shear_action = os.getenv("SHEAR_ACTION") if os.getenv("SHEAR_ACTION")  else "ban"
        if shear_action == "ban":
            await message.reply(await translate_async("🚫 You have been blocked from using this bot due to repeated violations of our guidelines.", lang1), reply_markup=ReplyKeyboardRemove())
            await add_bluser(user1)
            await delete_pair(user1)
            markup = await get_reply_markup(lang2)
            await cbot.send_message(user2, await translate_async("Chat has been Ended by the other user.", lang2), reply_markup= markup)
            await reset_profanity_scores(user1)
            await reset_profanity_scores(user2)
            return
        elif shear_action == "time-ban":
            await message.reply(await translate_async(f"🚫 You have been blocked for 2 hours from using this bot due to repeated violations of our guidelines.", lang1), reply_markup=ReplyKeyboardRemove())
            await add_bluser(user1)
            await delete_pair(user1)
            markup = await get_reply_markup(lang2)
            await cbot.send_message(user2, await translate_async("Chat has been Ended by the other user.", lang2), reply_markup= markup)
            await reset_profanity_scores(user1)
            await reset_profanity_scores(user2)
            await asyncio.sleep(3600)
            await unblock_user(int(user1))
            await message.reply(await translate_async(f"🔓 You have been unblocked and can now use this bot again. Please ensure that you follow our guidelines to avoid future blocks. Happy to assist you!", lang1))
            return

 # function to remove the user id after the chat ends.
async def reset_profanity_scores(user_id):
    if user_id in profanity_scores:
        del profanity_scores[user_id]


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


@cbot.on_callback_query(filters.regex(r"request_chat_(\d+)"))
async def request_chat_callback(_, callback_query: CallbackQuery):
    friend_id = int(callback_query.data.split("_")[2])
    user_id = callback_query.from_user.id
    user_name = await get_user_name(user_id)
    user_language = find_language(user_id)
    friend_language = find_language(friend_id)

    if is_chatting(user_id, callback_query.message, user_language):
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", user_language))]], resize_keyboard=True, one_time_keyboard=True)
        tr_txt = await translate_async("You are already in a chat. End the chat first by using below button!", user_language)
        await callback_query.message.reply(tr_txt, reply_markup= keyboard)
        return

    if is_user_searching(user_id):
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", user_language))]], resize_keyboard=True, one_time_keyboard=True)
        tr_txt = await translate_async("You are already searching. Stop searching first by using below button!", user_language)
        await callback_query.message.reply(tr_txt,  reply_markup= keyboard)
        return
    
    if is_user_searching(friend_id):
        tr_txt = await translate_async("You friend is already searching for anyone!", user_language)
        await callback_query.message.reply(tr_txt,  reply_markup= keyboard)
        return

    if is_chatting(friend_id, callback_query.message, friend_language):
        tr_txt = await translate_async("Your friend is already chatting with someone!", user_language)
        await callback_query.message.reply(tr_txt,  reply_markup= keyboard)
        return
    try:
        tr_txt = await translate_async("Your friend {} wants to chat with you. Do you want to chat with him?", friend_language)
        keyboard = [[InlineKeyboardButton(await translate_async("Yes, start chat!", friend_language), callback_data=f"accept_chat_{user_id}"), 
                    InlineKeyboardButton(await translate_async("No, not now!", friend_language), callback_data=f"decline_chat_{user_id}")]]
        await cbot.send_message(friend_id, tr_txt.format(user_name), reply_markup=InlineKeyboardMarkup(keyboard))
        await callback_query.message.reply(text = await translate_async("Yoo! 🤩 Your chat request has been sent to your friend! 📲 Now it's their turn to join the party! 🎉 If they accept, the dialogue will begin shortly! ⏱️ Stay tuned for the green light, and we'll get this chat started! 💚👫", user_language))
    except Exception as e:
        print(f"An exception occured while sending chat request to a friend: {e}")
        await callback_query.message.reply(f"{await translate_async("Failed to send chat request.", user_language)}")

@cbot.on_callback_query(filters.regex(r"accept_chat_(\d+)"))
async def accept_chat_callback(client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split("_")[2])
    my_id = callback_query.from_user.id
    new_pair = (user_id, my_id)
    add_pair(new_pair)
    motel1 = vip_users_details(user_id, "total_dialog")
    motel2 = vip_users_details(my_id, "total_dialog")
    total1 = motel1 if motel1 else 0
    total2 = motel2 if motel2 else 0
    save_premium_user(user_id, total_dialog=total1 + 1)
    save_premium_user(my_id, total_dialog=total2 + 1)
    start_stamp[f"user_{user_id}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    start_stamp[f"user_{my_id}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    message_timestamps[f"user_{user_id}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    message_timestamps[f"user_{my_id}"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    lang1 = find_language(user_id)
    lang2 = find_language(my_id)
    name1 = await get_user_name(user_id)
    name2 = await get_user_name(my_id)
    verify_status1 = vip_users_details(user_id, "verified") if vip_users_details(user_id, "verified") else "False"
    verify_status2 = vip_users_details(my_id, "verified") if vip_users_details(my_id, "verified") else "False"
    keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", lang1))]], resize_keyboard=True, one_time_keyboard=True)
    cap1 = await interlocutor_vip_message(lang1, name2, get_gender(my_id, lang2), get_age_group(my_id, lang2), verify_status2)
    await cbot.send_message(user_id, cap1, reply_markup=keyboard)
    caption = await interlocutor_vip_message(lang2, name1, get_gender(user_id, lang1), get_age_group(user_id, lang1), verify_status1)
    await callback_query.edit_message_text(caption, reply_markup=keyboard)

@cbot.on_callback_query(filters.regex(r"decline_chat_(\d+)"))
async def decline_chat_callback(client, callback_query):
    tr_txt = await translate_async("Chat request declined.", callback_query.from_user.language)
    await callback_query.message.edit_text(tr_txt)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


# function to check for inactive chats
async def check_inactive_chats():
    for pair in chat_pairs:
        if not pair:
            return
        user1, user2 = pair
        last_message_time1 = datetime.strptime(message_timestamps.get(f"user_{user1}"), "%Y-%m-%d %H:%M:%S")
        last_message_time2 = datetime.strptime(message_timestamps.get(f"user_{user2}"), "%Y-%m-%d %H:%M:%S")
        cr_time = datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "%Y-%m-%d %H:%M:%S")
        if last_message_time1 and last_message_time2:
            if (cr_time - last_message_time1).seconds > 60 and (cr_time - last_message_time2).seconds > 60:
                # Chat has been inactive for more than 10 minutes, end the chat
                await delete_pair(user1)
                await reset_profanity_scores(user1)
                await reset_profanity_scores(user2)
                lang1 = find_language(user1)
                lang2 = find_language(user2)
                reply_markup1 = await get_reply_markup(lang1)
                reply_markup2 = await get_reply_markup(lang2)
                caption1 = await translate_async("Chat has been ended due to inactivity.", lang1)
                caption2 = await translate_async("Chat has been ended due to inactivity.", lang2)
                await cbot.send_message(user1, caption1, reply_markup=reply_markup1)
                await cbot.send_message(user2, caption2, reply_markup=reply_markup2)


# Schedule the task to run every 1 minute
scheduler.add_job(check_inactive_chats, 'interval', minutes=1)
