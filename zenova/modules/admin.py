import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import json

from config import ADMIN_IDS
from zenova import zenova
from zenova import mongodb as collection
from config import key
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

@zenova.on_callback_query(filters.regex(r'^st_close$'))
async def close_page(_, query):
    try:
        # Delete the callback message
        await query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

@zenova.on_callback_query(filters.regex(r'^st_back$'))
async def back_page(_, query):
    try:
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text('Please choose an option:', reply_markup=reply_markup)
    except Exception as e:
        print("Error in close_profile:", e)

# Function to fetch user data from MongoDB
def get_user_data(collection):
    document = collection.find_one({})
    if document:
        return document
    else:
        return {}

def process_data(data, key_field='_id'):
    processed_data = {}
    for item in data:
        if key_field not in item:
            raise ValueError(f"Key field '{key_field}' not found in item {item}")
        key = str(item[key_field])
        if key not in processed_data:
            processed_data[key] = {}
        for field, value in item.items():
            if field == key_field:
                continue
            if field not in processed_data[key]:
                processed_data[key][field] = {}
            if isinstance(value, list):
                for i, item in enumerate(value):
                    if i not in processed_data[key][field]:
                        processed_data[key][field][i] = {}
                    for subfield, subvalue in item.items():
                        if subfield not in processed_data[key][field][i]:
                            processed_data[key][field][i][subfield] = []
                        processed_data[key][field][i][subfield].append(subvalue)
            else:
                processed_data[key][field][field] = value
    return processed_data

# Function to write user data to a file
def write_user_data_to_file(users_data):
    with open("Users_Data.txt", "w") as file:
        file.write(str(users_data))

# Callback handler for 'List of users' option
@zenova.on_callback_query(filters.regex(r'^list_users$'))
async def list_users_handler(_, query):
    # Retrieve user data from MongoDB collections
    raw_data = collection.find_one({key: {"$exists": True}})
    processed_data = process_data(raw_data)
    # Write user data to a file
    write_user_data_to_file(processed_data)

    # Send the file to the admin
    await query.message.reply_document(
        document="Users_Data.txt",
        caption="Here is the detailed list of users!"
    )

    # Remove the file after sending it
    os.remove("Users_Data.txt")


@zenova.on_callback_query(filters.regex(r'^delete_inactive$'))
async def delete_inactive_handler(_, query):
    await query.message.edit_text(text="You selected Delete inactive.")

@zenova.on_callback_query(filters.regex(r'^cancel$'))
async def cancel_handler(_, query):
    await query.message.edit_text(text="You canceled the operation.")

@zenova.on_callback_query(filters.regex(r'^st_close$'))
async def close_menu(client, callback_query):
    try:
        # Delete the callback message
        await callback_query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

@zenova.on_callback_query(filters.regex(r'^st_back$'))
async def back_menu(_, query):
    try:
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text('Please choose an option:', reply_markup=reply_markup)  
    except Exception as e:
        print("Error in back_profile:", e)