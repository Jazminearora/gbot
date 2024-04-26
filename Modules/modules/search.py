from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
    searching_users.append((message.from_user.id, user_language))  # Add user to searching list
    await message.reply_text("Your language: {}\nClick the search button to find an interlocutor.".format(user_language))
    # Create inline keyboard with stop button
    keyboard = [[InlineKeyboardButton("Stop Searching", callback_data='stop_search'), InlineKeyboardButton("Search", callback_data='search')]]
    await message.reply_text("Searching for an interlocutor...", reply_markup=InlineKeyboardMarkup(keyboard))

# Handle stop search button
@cbot.on_callback_query(filters.regex('^stop_search$'))
async def stop_search(_, query):
    user_id = query.from_user.id
    # Remove user from searching list
    for i, (user, _) in enumerate(searching_users):
        if user == user_id:
            del searching_users[i]
            break
    await query.answer("Search stopped.")

# Handle search button
@cbot.on_callback_query(filters.regex('^search$'))
async def search(_, query):
    user_id = query.from_user.id
    # Check if user is already in a chat
    for pair in chat_pairs:
        if user_id in pair:
            await query.answer("You are already in a chat.")
            return
    # Check if user is already searching
    for user, _ in searching_users:
        if user == user_id:
            await query.answer("You are already searching.")
            return
    # Add user to searching list
    user_language = find_language(user_id)
    searching_users.append((user_id, user_language))
    await query.answer("Searching for an interlocutor...")

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
            keyboard = [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
            await cbot.send_message(user1, "Chatting with user...", reply_markup=InlineKeyboardMarkup(keyboard))
            await cbot.send_message(user2, "Chatting with user...", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            # If languages don't match, put users back in the searching list
            searching_users.append((user1, lang1))
            searching_users.append((user2, lang2))
            await cbot.send_message(user1, "No interlocutor found. Please wait for a matching user.")
            await cbot.send_message(user2, "No interlocutor found. Please wait for a matching user.")

# Handle cancel button
@cbot.on_callback_query(filters.regex('^cancel$'))
async def cancel(_, query):
    user_id = query.from_user.id
    # Remove user from chat pairs
    for i, pair in enumerate(chat_pairs):
        if user_id in pair:
            del chat_pairs[i]
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
                await cbot.forward_messages(user2, message.chat.id, [message.message_id])
            else:
                await cbot.forward_messages(user1, message.chat.id, [message.message_id])
            break