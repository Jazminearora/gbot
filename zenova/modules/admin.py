from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from zenova import zenova, language_collection, gender_collection, age_group_collection, interests_collection
from helpers.helper import get_gender, get_age_group, get_interest, user_registered
from langdb import English, Russian, Ajerbejani
from config import ADMIN_IDS

async def add_user_id_to_collection(collection, document_id, user_id):
    update_query = {"$push": {document_id: user_id}}
    collection.update_one({}, update_query, upsert=True)

async def get_language(user_id):
    user_languages = language_collection.find_one({})
    for lang, users in user_languages.items():
        if isinstance(users, list) and user_id in users:
            return lang
    return "English"  # Default language if not found

@Client.on_message(filters.command("admin") & filters.user(ADMIN_IDS)) 
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

@Client.on_callback_query()
async def button_click(_, query):
    if query.data == 'newsletter':
        await query.message.edit_text(text="You selected Newsletter.")
    elif query.data == 'subscriptions':
        await query.message.edit_text(text="You selected Subscriptions.")
    elif query.data == 'impressions':
        await query.message.edit_text(text="You selected Impressions.")
    elif query.data == 'statistics':
        await query.message.edit_text(text="You selected Statistics.")
    elif query.data == 'referral':
        await query.message.edit_text(text="You selected Referral link.")
    elif query.data == 'vip_users':
        await query.message.edit_text(text="You selected VIP Users.")
    elif query.data == 'list_users':
        await query.message.edit_text(text="You selected List of users.")
    elif query.data == 'delete_inactive':
        await query.message.edit_text(text="You selected Delete inactive.")
    elif query.data == 'cancel':
        await query.message.edit_text(text="You canceled the operation.")

# Initialize your Pyrogram client and add appropriate filters...

# Start the client
