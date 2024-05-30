import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import pyrostep

from Modules import cbot, BOT_ID
from helpers.filters import is_member

pyrostep.listen(cbot)
os.environ['PROMO_STATUS'] = "True" # by default true

@cbot.on_callback_query(filters.regex(r'^subscriptions$'))
async def subscriptions_handler(_, query):
    chat_ids = get_chat_ids()
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕Add Chat", callback_data="add_chat"),
        InlineKeyboardButton("➖Delete Chat", callback_data="delete_chat")],
        [InlineKeyboardButton(f"🔄Set to {'🟢True' if (os.environ.get('PROMO_STATUS')) == "False" else '🔴False'}", callback_data="set_status")],
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]
    ])
    text = f"Current Chat IDs: {chat_ids}\nStatus: {os.environ.get('PROMO_STATUS', 'False')}"
    await query.message.edit_text(text=text, reply_markup=markup)


@cbot.on_callback_query(filters.regex(r'^add_chat$'))
async def add_chat_handler(client, query):
    await query.message.reply("Enter chat ID to add:")
    chat_id = await pyrostep.wait_for(query.from_user.id)
    try:
        chk = await is_member(client, chat_id.text, BOT_ID)
        if chk:
            name = (await cbot.get_chat(chat_id.text)).title
        else:
            await query.message.reply("It seems that it is not a valid chat id. If you believe it is correct, add me to that group/channel as admin first.")
            return
    except Exception as e:
        await query.message.reply(f"An error occured while validating chat id:\n\n{e}")
        return
    add_chat_id(chat_id.text)
    await query.answer(f"Chat: {name} added successfully!", show_alert=True)


@cbot.on_callback_query(filters.regex(r'^delete_chat$'))
async def delete_chat_handler(_, query):
    sk = await query.message.reply("Enter chat ID to delete:")
    chat_id = await pyrostep.wait_for(query.from_user.id)
    delete_chat_id(chat_id.text)
    await query.answer("Chat ID deleted successfully!", show_alert=True)


@cbot.on_callback_query(filters.regex(r'^set_status$'))
async def set_status_handler(_, query):
    promo_status = os.environ.get('PROMO_STATUS') if  os.environ.get('PROMO_STATUS') else "False"
    promo_status = "True" if  promo_status == "False" else "False" # toggle status
    os.environ['PROMO_STATUS'] = promo_status
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕Add Chat", callback_data="add_chat"),
        InlineKeyboardButton("➖Delete Chat", callback_data="delete_chat")],
        [InlineKeyboardButton(f"🔄Set to {'🟢True' if promo_status == "False" else '🔴False'}", callback_data="set_status")],
        [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
        InlineKeyboardButton(text="Close ❌", callback_data="st_close")]
    ])
    chat_ids = get_chat_ids()
    text = f"Current Chat IDs: {chat_ids}\nStatus: {promo_status}"
    await edit_message(query, text, markup)

async def edit_message(query, text, markup):
    await query.message.edit_text(text, reply_markup=markup)


def add_chat_id(chat_id):
    if 'SUBSCRIPTION' not in os.environ:
        os.environ['SUBSCRIPTION'] = ','.join([chat_id])
    else:
        current_subscription = os.environ['SUBSCRIPTION']
        new_subscription = ','.join([current_subscription, chat_id])
        os.environ['SUBSCRIPTION'] = new_subscription

def delete_chat_id(chat_id):
    if 'SUBSCRIPTION' in os.environ:
        current_subscription = os.environ['SUBSCRIPTION']
        new_subscription = ','.join([sub_id for sub_id in current_subscription.split(',') if sub_id != chat_id])
        if new_subscription:
            os.environ['SUBSCRIPTION'] = new_subscription
        else:
            del os.environ['SUBSCRIPTION']

def get_chat_ids():
    if 'SUBSCRIPTION' in os.environ:
        current_subscription = os.environ['SUBSCRIPTION']
        return current_subscription
    else:
        return ''