from pyrogram import Client, filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
import re
from helpers.helper import find_language
from helpers.translator import translate_async
import asyncio
from Modules import cbot


# List to store users searching for an interlocutor
searching_users = []

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
    text = "Searching users:\n" + str(searching_users) + "\n\nChat pairs:\n" + str(chat_pairs)
    await message.reply(text)

button_pattern = re.compile(r"^(🔍 (Search for an interlocutor|Найти собеседника|Məqalə axtar) 🔎)$")

@cbot.on_message(filters.private & filters.regex(button_pattern))
async def search_interlocutor(client, message):
    user_language = find_language(message.from_user.id)  # Retrieve user's language
    # Create keyboard with start searching button
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Start Searching")]])
    await message.reply("Your language: {}\nClick the start searching button to find an interlocutor.".format(user_language), reply_markup = keyboard)

# Handle start search button
@cbot.on_message(filters.private & filters.regex("Start Searching"))
async def start_search(client, message):
    user_id = message.from_user.id
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
    # Add user to searching list
    user_language = find_language(user_id)
    searching_users.append({"user_id": user_id, "language": user_language})
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Stop Searching")]], resize_keyboard= True, one_time_keyboard= True)
    await message.reply("Searching for an interlocutor...", reply_markup = keyboard)

# Handle stop search button
@cbot.on_message(filters.private & filters.regex("Stop Searching"))
async def stop_search(client, message):
    user_id = message.from_user.id
    # Remove user from searching list
    for i, user in enumerate(searching_users):
        if user["user_id"] == user_id:
            del searching_users[i]
            break
    await message.reply("Search stopped.")

# Function to match users and start chatting
async def match_users():
    while len(searching_users) >= 2:
        user1 = searching_users.pop(0)
        user2 = searching_users.pop(0)
        if user1["language"] == user2["language"]:
            add_pair([user1["user_id"], user2["user_id"]])  # Add pair to chat_pairs list
            await cbot.send_message(user1["user_id"], "Interlocutor found! You can start chatting now.")
            await cbot.send_message(user2["user_id"], "Interlocutor found! You can start chatting now.")
            # Create keyboard with cancel button
            keyboard = ReplyKeyboardMarkup([[KeyboardButton("Cancel")]], resize_keyboard= True, one_time_keyboard= True)
            await cbot.send_message(user1["user_id"], "Chatting with user...", reply_markup=keyboard)
            await cbot.send_message(user2["user_id"], "Chatting with user...", reply_markup=keyboard)
        else:
            # If languages don't match, put users back in the searching list
            searching_users.append(user1)
            searching_users.append(user2)
            await cbot.send_message(user1["user_id"], "No interlocutor found. Please wait for a matching user.")
            await cbot.send_message(user2["user_id"], "No interlocutor found. Please wait for a matching user.")

# Handle cancel button
@cbot.on_message(filters.private & filters.regex("Cancel"))
async def cancel(_, message):
    user_id = message.from_user.id
    # Find the chat pair and delete it
    if delete_pair(user_id):
        await message.reply("Chat cancelled.")
        # Find the other user in the pair and inform them
        for pair in chat_pairs:
            if user_id in pair:
                other_user_id = pair[1] if pair[0] == user_id else pair[0]
                await cbot.send_message(other_user_id, "Chat has been stopped by the other user.")
                break

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
