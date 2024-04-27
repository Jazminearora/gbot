from pyrogram import Client, filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
import re
from helpers.helper import find_language, get_gender, get_age_group, get_interest
from database.premiumdb import is_user_premium, vip_users_details
from helpers.translator import translate_async
import asyncio
from Modules import cbot


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
    text = "Searching users:\n" + str(searching_users) + "\n\nChat pairs:\n" + str(chat_pairs) + "\n\nPremium users:\n" + str(searching_premium_users)
    await message.reply(text)

button_pattern = re.compile(r"^(🔍 (Search for an interlocutor|Найти собеседника|Məqalə axtar) 🔎)$")

@cbot.on_message(filters.private & filters.regex(button_pattern))
async def search_interlocutor(client, message):
    user_language = find_language(message.from_user.id)  # Retrieve user's language
    # Create keyboard with start searching button
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Start Searching")]], resize_keyboard=True, one_time_keyboard=True)
    await message.reply("Your language: {}\nClick the start searching button to find an interlocutor.".format(user_language), reply_markup=keyboard)

# Handle start search button
@cbot.on_message(filters.private & filters.regex("Start Searching"))
async def start_search(client, message):
    user_id = message.from_user.id
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        print(await is_user_premium(user_id))
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                await message.reply("You are already in a chat.")
                return
        # Check if user is already searching
        for user in searching_premium_users:
            if user["user_id"] == user_id:
                await message.reply("You are already searching.")
                return
        # Get premium user's configuration
        gender = await vip_users_details(user_id, "gender")
        age_groups = await vip_users_details(user_id, "age_groups")
        room = await vip_users_details(user_id, "room")
        language = find_language(user_id)
        searching_premium_users.append({"user_id": user_id, "language": language, "gender": gender, "age_groups": age_groups, "room": room})
        keyboard = ReplyKeyboardMarkup([[KeyboardButton("Stop Searching")]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply("Searching for an interlocutor...", reply_markup=keyboard)
    else:
        # Check if user is already in a chat
        for pair in chat_pairs:
            if user_id in pair:
                await message.reply("You are already in a chat.")
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
        keyboard = ReplyKeyboardMarkup([[KeyboardButton("Stop Searching")]], resize_keyboard=True, one_time_keyboard=True)
        await message.reply("Searching for an interlocutor...", reply_markup=keyboard)

# Handle stop search button
@cbot.on_message(filters.private & filters.regex("Stop Searching"))
async def stop_search(client, message):
    user_id = message.from_user.id
    # Remove user from searching list
    for i, user in enumerate(searching_users):
        if user["user_id"] == user_id:
            del searching_users[i]
            break
    for i, user in enumerate(searching_premium_users):
        if user["user_id"] == user_id:
            del searching_premium_users[i]
            break
    await message.reply("Search stopped.", reply_markup=ReplyKeyboardRemove())

# Function to match users and start chatting
async def match_users():
    while True:
        # Match premium users with normal users
        for premium_user in searching_premium_users.copy():
            for normal_user in searching_users.copy():
                if (premium_user["language"] == normal_user["language"] and
                    premium_user["gender"] == normal_user["gender"] and
                    set(premium_user["age_groups"]) & set(normal_user["age_groups"]) and
                    premium_user["room"] == normal_user["room"]):
                    # Match found, add pair to chat_pairs and notify users
                    new_pair = (premium_user["user_id"], normal_user["user_id"])
                    add_pair(new_pair)
                    await cbot.send_message(premium_user["user_id"], "Interlocutor found! You can start chatting now.")
                    await cbot.send_message(normal_user["user_id"], "Interlocutor found! You can start chatting now.")
                    # Remove users from searching lists
                    searching_premium_users.remove(premium_user)
                    searching_users.remove(normal_user)
                    break

        # Match normal users with other normal users
        for i, user1 in enumerate(searching_users.copy()):
            for j, user2 in enumerate(searching_users[i+1:].copy(), i+1):
                if (user1["language"] == user2["language"]):
                    # Match found, add pair to chat_pairs and notify users
                    new_pair = (user1["user_id"], user2["user_id"])
                    add_pair(new_pair)
                    await cbot.send_message(user1["user_id"], "Interlocutor found! You can start chatting now.")
                    await cbot.send_message(user2["user_id"], "Interlocutor found! You can start chatting now.")
                    # Remove users from searching lists
                    searching_users.remove(user1)
                    searching_users.remove(user2)
                    break
        await asyncio.sleep(1)  # Check every 1 second


# Handle cancel button
@cbot.on_message(filters.private & filters.regex("Cancel"))
async def cancel(_, message):
    user_id = message.from_user.id
    # Find the other user in the pair and inform them
    for pair in chat_pairs:
        if user_id in pair:
            other_user_id = pair[1] if pair[0] == user_id else pair[0]
            await cbot.send_message(other_user_id, "Chat has been stopped by the other user.", reply_markup=ReplyKeyboardRemove())
            break
    # Find the chat pair and delete it
    if delete_pair(user_id):
        await message.reply("Chat cancelled.", reply_markup=ReplyKeyboardRemove())

# Periodically check for matched users
async def match_users_loop():
    while True:
        await match_users()
        await asyncio.sleep(5)  # Check every 5 seconds

# Start matching users loop
cbot.loop.create_task(match_users_loop())

# Handle incoming messages
@cbot.on_message(filters.private)
async def forward_message(client, message):
    for pair in chat_pairs:
        if message.from_user.id in pair:
            user1, user2 = pair
            if message.from_user.id == user1:
                await cbot.copy_message(user2, message.chat.id, message.id)
            else:
                await cbot.copy_message(user1, message.chat.id, message.id)
            break