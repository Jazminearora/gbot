from pyrogram import filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
import re
from helpers.helper import find_language, get_gender, get_age_group, get_interest
from helpers.forcesub import user_registered, subscribed
from database.premiumdb import is_user_premium, vip_users_details
from langdb.get_msg import get_reply_markup, interlocutor_vip_message, interlocutor_normal_message
from helpers.translator import translate_async
from Modules.modules.register import get_user_name
import asyncio
from Modules import cbot
from config import ADMINS
import concurrent.futures

# Create a ThreadPoolExecutor with 1 worker
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)


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
    try:
        text = await translate_async("Searching users:\n", language)+ str(searching_users) + "\n\nChat pairs:\n" + str(chat_pairs) + "\n\nPremium users:\n" + str(searching_premium_users)
    except:
        text = f"Searching users: {searching_users})" + "\n\nChat pairs:" + (chat_pairs) + "\n\nPremium users:" + (searching_premium_users)
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
        keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", language))]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply(await translate_async("Searching for an interlocutor...", language), reply_markup=keyboard)
        # sleep for 1 sec
        await asyncio.sleep(1) 
        searching_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": interest})

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


# Function to match users and start chatting
async def match_users():
    await match_premium_with_normal()
    await match_premium_with_premium()
    await match_normal_with_normal()

async def match_premium_with_normal():
    for premium_user in searching_premium_users.copy():
        for normal_user in searching_users.copy():
            if matches(premium_user, normal_user):
                await match_found(premium_user, normal_user)
                break

async def match_premium_with_premium():
    for i, premium_user1 in enumerate(searching_premium_users.copy()):
        for j, premium_user2 in enumerate(searching_premium_users[i+1:].copy(), i+1):
            if (premium_user1["language"] == find_language(premium_user2["user_id"]) and
                (premium_user1["gender"] == get_gender(premium_user2["user_id"], "huls") or premium_user1["gender"] == "any gender" or premium_user1["gender"] is None) and
                get_age_group(premium_user2["user_id"], "huls") in premium_user1["age_groups"] or premium_user1["age_groups"] is None and
                (premium_user1["room"] == premium_user2["room"] or premium_user1["room"] == "any" or premium_user1["room"] is None) and
                premium_user2["language"] == find_language(premium_user1["user_id"]) and
                (premium_user2["gender"] == get_gender(premium_user1["user_id"], "huls") or premium_user2["gender"] == "any gender" or premium_user2["gender"] is None) and
                get_age_group(premium_user1["user_id"], "huls") in premium_user2["age_groups"] or premium_user2["age_groups"] is None and
                (premium_user2["room"] == premium_user1["room"] or premium_user2["room"] == "any" or premium_user2["room"] is None)):
                await match_found(premium_user1, premium_user2)
                break

async def match_normal_with_normal():
    for i, user1 in enumerate(searching_users.copy()):
        for j, user2 in enumerate(searching_users[i+1:].copy(), i+1):
            if user1["language"] == user2["language"]:
                await match_found(user1, user2)
                break

def matches(user1, user2):
    return (user1["language"] == user2["language"] and
            (user1["gender"] == user2["gender"] or user1["gender"] == "any gender" or user1["gender"] is None) and
            (user2["age_groups"] in user1["age_groups"] or user1["age_groups"] is None) and
            (user1["room"] == user2["room"] or user1["room"] == "any" or user1["room"] is None))

async def match_found(user1, user2):
    new_pair = (user1["user_id"], user2["user_id"])
    add_pair(new_pair)
    await send_messages(user1, user2)
    searching_premium_users.remove(user1)
    searching_users.remove(user2)

async def send_messages(user1, user2):
    lang1 = find_language(user1["user_id"])
    lang2 = find_language(user2["user_id"])
    name1 = await get_user_name(user1["user_id"])
    name2 = await get_user_name(user2["user_id"])
    cap1 = interlocutor_vip_message(lang1, name2, {user2["gender"]}, {user2["age_groups"]})
    cap2 = interlocutor_vip_message(lang2, name1, {user1["gender"]}, {user1["age_groups"]})
    keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", lang1))]], resize_keyboard=True, one_time_keyboard=True)
    await cbot.send_message(user1["user_id"], cap1, reply_markup=keyboard)
    await cbot.send_message(user2["user_id"], cap2, reply_markup=keyboard)


# Handle cancel button
@cbot.on_message(filters.private & filters.regex("End chat|Söhbəti bitirin|Конец чат|Terminate Conversation") & subscribed & user_registered)
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
    # Find the chat pair and delete it
    if delete_pair(user_id):
        reply_markup = await get_reply_markup(language)
        await message.reply(await translate_async("Chat Ended.", language), reply_markup=reply_markup)

# Periodically check for matched users
async def match_users_loop():
    while True:
        # Submit the search_users function to the ThreadPoolExecutor
        executor.submit(await match_users)

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