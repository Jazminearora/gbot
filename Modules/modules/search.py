from pyrogram import filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import re
from helpers.helper import find_language, get_gender, get_age_group, get_interest
from helpers.forcesub import user_registered, subscribed
from database.premiumdb import is_user_premium, vip_users_details
from langdb.get_msg import get_reply_markup
from helpers.translator import translate_async
from Modules.modules.register import get_user_name
import asyncio
from Modules import cbot
from config import ADMINS


# List to store users searching for an interlocutor
searching_users = []
searching_premium_users = []

# List to store pairs of users for chatting
chat_pairs = []

# Function to delete a pair
def delete_pair(id_to_delete):
    global chat_pairs
    for i, pair in enumerate(chat_pairs):
        if id_to_delete in pair:
            del chat_pairs[i]
            return True
    return False

# Function to add a pair
def add_pair(new_pair):
    global chat_pairs
    chat_pairs.append(new_pair)

@cbot.on_message(filters.command("hlo"))
async def hlo(client, message):
    language = find_language(message.from_user.id)
    text = await translate_async("Searching users:\n", language)+ str(searching_users) + "\n\nChat pairs:\n" + str(chat_pairs) + "\n\nPremium users:\n" + str(searching_premium_users)
    await message.reply(text)

button_pattern = re.compile(r"^(🔍 (Search for an interlocutor|Найти собеседника|Məqalə axtar) 🔎)$")

@cbot.on_message(filters.private & filters.regex(button_pattern) & filters.private & subscribed & user_registered)
async def search_interlocutor(client, message):
    user_language = find_language(message.from_user.id)  # Retrieve user's language
    # Create keyboard with start searching button
    keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Start Searching", user_language))]], resize_keyboard=True, one_time_keyboard=True)
    caption = await translate_async("Your language:", user_language) + f"{user_language}\n" + await translate_async("Click the start searching button to find an interlocutor.", user_language)
    await message.reply(caption, reply_markup=keyboard)

# Handle start search button
@cbot.on_message(filters.private & filters.regex("Start Searching|Начать поиск|Axtarmağa başlayın") & subscribed & user_registered)
async def start_search(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                await message.reply(await translate_async("You are already in a chat.", language))
                return
        # Check if user is already searching
        for user in searching_premium_users:
            if user["user_id"] == user_id:
                await message.reply(await translate_async("You are already searching.", language))
                return
        # Get premium user's configuration
        gender = await vip_users_details(user_id, "gender")
        age_groups = await vip_users_details(user_id, "age_groups")
        room = await vip_users_details(user_id, "room")
        searching_premium_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": room})
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for an interlocutor...", language), reply_markup=keyboard)
    else:
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
        searching_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": None})
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for an interlocutor...", language), reply_markup=keyboard)

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

async def get_interlocutor_message(language, name, gender, age_group):
    if language == "English":
        message = f"Interlocutor found!\n\nUsers details:\nName: {name}\nGender: {gender}\nAge group: {age_group}\n\nYou can start chatting now."
    elif language == "Russian":
        message = f"Собеседник найден!\n\nДанные пользователя:\nИмя: {name}\nПол: {gender}\nВозрастная группа: {age_group}\n\nТеперь вы можете начать общение."
    elif language == "Azerbejani":
        message = f"Müşayiətçi tapıldı!\n\nİstifadəçinin məlumatları:\nAd: {name}\nCins: {gender}\nYaş qrupu: {age_group}\n\nSiz artıq söhbətə başlaya bilərsiniz."
    else:
        message = "Language not supported."
    return message

# Function to match users and start chatting
async def match_users():
    while True:
        matched = False  # Flag to check if any match occurred in this iteration
        # Match premium users with normal users
        for premium_user in searching_premium_users.copy():
            for normal_user in searching_users.copy():
                if (premium_user["language"] == normal_user["language"] and
                    (premium_user["gender"] == normal_user["gender"] or premium_user["gender"] == "any gender") and
                    normal_user["age_groups"] in premium_user["age_groups"] and
                    premium_user["room"] == normal_user["room"]):
                    # Match found, add pair to chat_pairs and notify users
                    new_pair = (premium_user["user_id"], normal_user["user_id"])
                    add_pair(new_pair)
                    name = await get_user_name(normal_user["user_id"])
                    lang1 = find_language(premium_user["user_id"])
                    cap1 = get_interlocutor_message(lang1, name, {normal_user["gender"]}, {normal_user["age_groups"]})
                    lang2 = find_language(normal_user["user_id"])
                    keyboard = ReplyKeyboardMarkup([[KeyboardButton(translate_async("End chat", lang1))]], resize_keyboard=True, one_time_keyboard=True)
                    await cbot.send_message(premium_user["user_id"], cap1, reply_markup= keyboard)
                    await cbot.send_message(normal_user["user_id"], await translate_async("Interlocutor found!\nPurchase Premium to know the details of Interlocutor😈! \n\nYou can start chatting now.", lang2), reply_markup= keyboard)
                    # Remove users from searching lists
                    searching_premium_users.remove(premium_user)
                    searching_users.remove(normal_user)
                    matched = True  # Set flag to True
                    break  # Break out of inner loop if match found
            if matched:  # Break out of outer loop if match found
                break


        # Match premium users with other premium users
        for i, premium_user1 in enumerate(searching_premium_users.copy()):
            for j, premium_user2 in enumerate(searching_premium_users[i+1:].copy(), i+1):
                if (premium_user1["language"] == find_language(premium_user2) and
                    (premium_user1["gender"] == get_gender(premium_user2, "huls") or premium_user1["gender"] == "any gender") and
                    get_age_group(premium_user2, "huls") in premium_user1["age_groups"] and
                    premium_user1["room"] == premium_user2["room"] and
                    premium_user2["language"] == find_language(premium_user1) and
                    (premium_user2["gender"] == get_gender(premium_user1, "huls") or premium_user2["gender"] == "any gender") and
                    get_age_group(premium_user1, "huls") in premium_user2["age_groups"] and
                    premium_user2["room"] == premium_user1["room"]):
                    # Match found, add pair to chat_pairs and notify users
                    new_pair = (premium_user1["user_id"], premium_user2["user_id"])
                    add_pair(new_pair)
                    name1 = await get_user_name(premium_user1["user_id"])
                    name2 = await get_user_name(premium_user2["user_id"])
                    lang1 = find_language(premium_user["user_id"])
                    keyboard = ReplyKeyboardMarkup([[KeyboardButton(translate_async("End chat", lang1))]], resize_keyboard=True, one_time_keyboard=True)
                    cap1 = get_interlocutor_message(lang1, name2, {premium_user2["gender"]}, {premium_user2["age_groups"]})
                    cap2 = get_interlocutor_message(lang2, name1, {premium_user1["gender"]}, {premium_user1["age_groups"]})
                    await cbot.send_message(premium_user1["user_id"], cap1, reply_markup= keyboard)
                    await cbot.send_message(premium_user2["user_id"], cap2, reply_markup= keyboard)
                    # Remove users from searching lists
                    searching_premium_users.remove(premium_user1)
                    searching_premium_users.remove(premium_user2)
                    matched = True  # Set flag to True
                    break  # Break out of inner loop if match found
                if matched:  # Break out of outer loop if match found
                    break

        # Match normal users with other normal users
        if not matched:  # Only if no match occurred with premium users
            for i, user1 in enumerate(searching_users.copy()):
                for j, user2 in enumerate(searching_users[i+1:].copy(), i+1):
                    if user1["language"] == user2["language"]:
                        # Match found, add pair to chat_pairs and notify users
                        new_pair = (user1["user_id"], user2["user_id"])
                        lang1 = find_language(user1)
                        lang2 = find_language(user2)
                        add_pair(new_pair)
                        keyboard = ReplyKeyboardMarkup([[KeyboardButton(translate_async("End chat", lang1))]], resize_keyboard=True, one_time_keyboard=True)
                        await cbot.send_message(user1["user_id"], await translate_async("Interlocutor found!\nPurchase Premium to know the details of Interlocutor😈! \n\nYou can start chatting now.", lang1), reply_markup= keyboard)
                        await cbot.send_message(user2["user_id"], await translate_async("Interlocutor found!\nPurchase Premium to know the details of Interlocutor😈! \n\nYou can start chatting now.", lang2), reply_markup=keyboard)
                        # Remove users from searching lists
                        searching_users.remove(user1)
                        searching_users.remove(user2)
                        matched = True  # Set flag to True
                        break  # Break out of inner loop if match found
                if matched:  # Break out of outer loop if match found
                    break
        await asyncio.sleep(1)  # Check every 1 second


# Handle cancel button
@cbot.on_message(filters.private & filters.regex("End chat|Söhbəti bitirin|Конец чат") & subscribed & user_registered)
async def cancel(_, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    # Find the other user in the pair and inform them
    for pair in chat_pairs:
        if user_id in pair:
            other_user_id = pair[1] if pair[0] == user_id else pair[0]
            other_user_lang = find_language(other_user_id)
            reply_markup2 = await get_reply_markup(other_user_lang)
            await cbot.send_message(other_user_id, await translate_async("Chat has been Ended by the other user.", other_user_lang), reply_markup=reply_markup2)
            break
    # Find the chat pair and delete it
    if delete_pair(user_id):
        reply_markup = await get_reply_markup(language)
        await message.reply(await translate_async("Chat Ended.", language), reply_markup=reply_markup)

# Periodically check for matched users
async def match_users_loop():
    while True:
        await match_users()
        await asyncio.sleep(5)  # Check every 5 seconds

# Start matching users loop
cbot.loop.create_task(match_users_loop())

# Handle incoming messages
@cbot.on_message(filters.private & subscribed & user_registered)
async def forward_message(client, message):
    for pair in chat_pairs:
        if message.from_user.id in pair:
            user1, user2 = pair
            lang1 = find_language(user1)
            lang2 = find_language(user2)
            if message.from_user.id == user1:
                is_premium, _ = await is_user_premium(user1)
                if is_premium:
                    await cbot.copy_message(user2, message.chat.id, message.id)
                else: 
                    if message.text:
                        await cbot.copy_message(user2, message.chat.id, message.id)
                    else:
                        await cbot.send_message(user1, await translate_async("Sorry, you need to be a premium user to send photos, videos, stickers, and documents. Purchase premium for full access.", lang1))
            elif message.from_user.id == user2:
                is_premium, _ = await is_user_premium(user2)
                if is_premium:
                    await cbot.copy_message(user1, message.chat.id, message.id)
                else:
                    if message.text:
                        await cbot.copy_message(user1, message.chat.id, message.id)
                    else:
                        await cbot.send_message(user2, await translate_async("Sorry, you need to be a premium user to send photos, videos, stickers, and documents. Purchase premium for full access.", lang2))

            break