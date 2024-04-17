import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Assuming you have ADMIN_IDS defined in your config module
from config import ADMIN_IDS
from zenova import zenova
from helpers.helper import get_total_users, find_language


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

home_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]])


# Command handler for /admin
@zenova.on_message(filters.command("admin") & filters.user(ADMIN_IDS))
async def admin_panel(_, message):

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
    # Get the user counts for each language
    eng_users = get_total_users("English") or 0
    russian_users = get_total_users("Russian") or 0
    azerbejani_users = get_total_users("Azerbejani") or 0
    total_users = eng_users + russian_users + azerbejani_users

    # Update the user_stats dictionary
    user_stats = {
        "eng_users": eng_users,
        "russian_users": russian_users,
        "azerbejani_users": azerbejani_users,
        "total_users": total_users
    }

    # Format the statistics text using string formatting
    stats_text = (
        "--Total stats of Bot--\n"
        f"Total users: {total_users} \n"
        f"English users: {eng_users}\n"
        f"Russian users: {russian_users}\n"
        f"Azerbejani users: {azerbejani_users}"
    )
    # Edit the message to display the statistics
    await query.message.edit_text(text=stats_text, reply_markup = home_btn)

    
@zenova.on_callback_query(filters.regex(r'^referral$'))
async def referral_handler(_, query):
    await query.message.edit_text(text="You selected Referral link.")

@zenova.on_callback_query(filters.regex(r'^vip_users$'))
async def vip_users_handler(_, query):
    await query.message.edit_text(text="You selected VIP Users.")

import os
from pyrogram.types import InputMediaDocument
from zenova import mongodb as database
from zenova import language_collection, gender_collection, age_group_collection, interests_collection


# Function to fetch user data from MongoDB
def get_user_data(collection):
    document = collection.find_one({})
    if document:
        return document
    else:
        return {}

# Function to write user data to a file
def write_user_data_to_file(users_data):
    with open("user_data.txt", "w") as file:
        for key, value in users_data.items():
            file.write(f"{key}:\n")
            for user in value:
                file.write(f"- {user}\n")

# Callback handler for 'List of users' option
@zenova.on_callback_query(filters.regex(r'^list_users$'))
async def list_users_handler(_, query):
    # Retrieve user data from MongoDB collections
    language_data = get_user_data(language_collection)
    gender_data = get_user_data(gender_collection)
    age_group_data = get_user_data(age_group_collection)
    interests_data = get_user_data(interests_collection)

    # Combine user data from different collections
    users_data = {
        "Language": language_data,
        "Gender": gender_data,
        "Age Group": age_group_data,
        "Interests": interests_data
    }

    # Write user data to a file
    write_user_data_to_file(users_data)

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
