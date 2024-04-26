from pyrogram import Client, filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import re
from helpers.helper import find_language
from helpers.translator import translate_async
import asyncio
from Modules import cbot

# List to store users searching for an interlocutor
searching_users = []

# List to store pairs of users for chatting
chat_pairs = []

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
    for user, _ in searching_users:
        if user == user_id:
            await message.reply("You are already searching.")
            return
    # Add user to searching list
    user_language = find_language(user_id)
    searching_users.append((user_id, user_language))
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Stop Searching")]])
    await message.reply("Searching for an interlocutor...", reply_markup = keyboard)

# Handle stop search button
@cbot.on_message(filters.private & filters.regex("Stop Searching"))
async def stop_search(client, message):
    user_id = message.from_user.id
    # Remove user from searching list
    for i, (user, _) in enumerate(searching_users):
        if user == user_id:
            del searching_users[i]
            break
    await message.reply("Search stopped.")

# Function to match users and start chatting
async def match_users():
    while len(searching_users) >= 2:
        user1, lang1 = searching_users.pop(0)
        user2, lang2 = searching_users.pop(0)
        if lang1 == lang2:
            chat_pairs.append((user1, user2))
            await cbot.send_message(user1, "Interlocutor found! You can start chatting now.")
            await cbot.send_message(user2, "Interlocutor found! You can start chatting now.")
            # Create inline keyboard with cancel button
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data='cancel')]])
            await cbot.send_message(user1, "Chatting with user...", reply_markup=keyboard)
            await cbot.send_message(user2, "Chatting with user...", reply_markup=keyboard)
        else:
            # If languages don't match, put users back in the searching list
            searching_users.append((user1, lang1))
            searching_users.append((user2, lang2))
            await cbot.send_message(user1, "No interlocutor found. Please wait for a matching user.")
            await cbot.send_message(user2, "No interlocutor found. Please wait for a matching user.")

# Handle cancel button
@cbot.on_callback_query(filters.regex('^cancel$'))
async def cancel(_,query):
    user_id = query.from_user.id
    # Remove user from chat pairs
    for i, pair in enumerate(chat_pairs):
        if user_id in pair:
            del chat_pairs[i]
            break
    # Remove user from searching list
    for i, (user, _) in enumerate(searching_users):
        if user == user_id:
            del searching_users[i]
            break
    await query.answer("Chat cancelled.")

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
                await cbot.copy_message(user2, message.chat.id, [message.id])
            else:
                await cbot.copy_message(user1, message.chat.id, [message.id])
            break



