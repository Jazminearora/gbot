import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Assuming you have ADMIN_IDS defined in your config module
from config import ADMIN_IDS
from zenova import zenova

# Command handler for /admin
@zenova.on_message(filters.command("admin") & filters.user(ADMIN_IDS))
async def admin_panel(_, message):
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
            InlineKeyboardButton("⛓ Referral link", callback_data='referral'),
            InlineKeyboardButton("👑 VIP Users", callback_data='vip_users')
        ],
        [
            InlineKeyboardButton("👥 List of users", callback_data='list_users'),
            InlineKeyboardButton("♿️ Delete inactive", callback_data='delete_inactive')
        ],
        [
            InlineKeyboardButton("🚫 Cancel", callback_data='cancel')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text('Please choose an option:', reply_markup=reply_markup)

# Callback handler using regex filter
@zenova.on_callback_query(filters.regex(r'^newsletter$'))
async def newsletter_handler(_, query):
    await query.message.edit_text(text="You selected Newsletter.")

@zenova.on_callback_query(filters.regex(r'^subscriptions$'))
async def subscriptions_handler(_, query):
    await query.message.edit_text(text="You selected Subscriptions.")

@zenova.on_callback_query(filters.regex(r'^impressions$'))
async def impressions_handler(_, query):
    await query.message.edit_text(text="You selected Impressions.")

@zenova.on_callback_query(filters.regex(r'^statistics$'))
async def statistics_handler(_, query):
    # Example data, replace with your actual data retrieval logic
    total_users = 1000
    eng_users = 700
    russian_users = 200
    azerbejani_users = 100

    # Format the statistics
    stats_text = (
        f"<b>Total stats of Bot</b>\n"
        f"Total users: {total_users}\n"
        f"English users: {eng_users}\n"
        f"Russian users: {russian_users}\n"
        f"Azerbejani users: {azerbejani_users}"
    )

    # Edit the message to display the statistics
    await query.message.edit_text(text=stats_text, parse_mode="HTML")
    
@zenova.on_callback_query(filters.regex(r'^referral$'))
async def referral_handler(_, query):
    await query.message.edit_text(text="You selected Referral link.")

@zenova.on_callback_query(filters.regex(r'^vip_users$'))
async def vip_users_handler(_, query):
    await query.message.edit_text(text="You selected VIP Users.")

import os
from pyrogram.types import InputMediaDocument


def get_user_data():
    # Assuming you have a method to fetch user data from your database
    # Replace this with your actual database query logic
    document = collection.find_one({key: {"$exists": True}})
    users_data = document.get(key, {})
    return users_data

# Function to write user data to a file
def write_user_data_to_file(users_data):
    with open("user_data.txt", "w") as file:
        for language, users in users_data.items():
            file.write(f"{language}:\n")
            for user in users:
                file.write(f"- {user}\n")


# Callback handler for 'List of users' option
@zenova.on_callback_query(filters.regex(r'^list_users$'))
async def list_users_handler(_, query):
    users_data = get_user_data()  # Retrieve user data from the database
    write_user_data_to_file(users_data)  # Write user data to a file

    # Send the file to the admin
    await query.message.reply_document(
        document="user_data.txt",
        caption="Here is the list of users."
    )

    # Remove the file after sending it
    os.remove("user_data.txt")

@zenova.on_callback_query(filters.regex(r'^delete_inactive$'))
async def delete_inactive_handler(_, query):
    await query.message.edit_text(text="You selected Delete inactive.")

@zenova.on_callback_query(filters.regex(r'^cancel$'))
async def cancel_handler(_, query):
    await query.message.edit_text(text="You canceled the operation.")
