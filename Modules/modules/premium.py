from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import urllib.parse
import asyncio
from AaioAPI import AsyncAaioAPI

from helpers.helper import find_language
from helpers.translator import translate_async
from database.premiumdb import extend_premium_user_hrs
from langdb.get_msg import get_premium_msg
from database.referdb import get_point

from Modules import cbot , BOT_USERNAME
from config import MERCHANT_ID, MERCHANT_KEY, API_KEY

button_pattern = re.compile(r"^💎 (Premium|Премиум|Premium) 💎$")
@cbot.on_message(filters.private & filters.regex(button_pattern))
async def premium_option(client, message):
    user_id = message.from_user.id
    user_lang = find_language(user_id)
    caption, buttons = await get_premium_msg(user_lang)
    await message.reply_text(caption, reply_markup=buttons)

async def get_text(total_points, referral_link, language):
    msg = "Invite users using your link and receive 👑VIP status for 1 hour for each!\n\nInvited:"
    msg2 = "Your personal link:\n👉"
    share_txt = "Hey buddy!!\n\n Try this amazing bot for getting connected with strangers from the world!"
    
    translated_msg = await translate_async(msg, target_language=language)
    translated_msg2 = await translate_async(msg2, target_language=language)
    translated_share_txt = await translate_async(share_txt, target_language=language)
    
    message = (
        translated_msg + str(total_points) + "\n\n" +
        translated_msg2 + referral_link
    )
    return message, translated_share_txt

@cbot.on_callback_query(filters.regex("^prem_free$"))
async def premium_free_callback(bot, update):
    # Your logic here to handle the callback query
    user_id = update.from_user.id
    total_points = await get_point(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start=r{user_id}"
    
    user_lang = find_language(user_id)
    caption, share_txt = await get_text(total_points, referral_link, user_lang)
    
    encoded_share_txt = urllib.parse.quote(share_txt)
    share_link = f"https://t.me/share/url?url={referral_link}&text={encoded_share_txt}"
    print("share link:", share_link)
    
    refer_button_text = await translate_async("Refer your Friend", target_language=user_lang)
    
    await update.message.edit_text(
        text=caption,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(refer_button_text, url=share_link)]]
        )
    )

@cbot.on_message(filters.command(["referals"]) & filters.private)
async def referals_command(client, message):
    user_id = message.from_user.id
    total_points = await get_point(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start=r{user_id}"
    
    user_lang = find_language(user_id)
    caption , share_txt = await get_text(total_points, referral_link, user_lang)

    
    encoded_share_txt = urllib.parse.quote(share_txt)
    share_link = f"https://t.me/share/url?url={referral_link}&text={encoded_share_txt}"
    print("share link:", share_link)
    refer_button_text = await translate_async("Refer your Friend", target_language=user_lang)
    await message.reply_text(
        text=caption,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(refer_button_text, url=referral_link)]]
        )
    )




@cbot.on_callback_query(filters.regex(r"premium_"))
async def premium_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    if data == "premium_1_day":
        amount = 1.08
        extend_hrs = 24
    elif data == "premium_3_days":
        amount = 2.15
        extend_hrs = 72
    elif data == "premium_1_week":
        amount = 8.61
        extend_hrs = 168
    elif data == "premium_1_month":
        amount = 12.98
        extend_hrs = 720

    order_id = f"premium_{user_id}_{data}"
    lang = "en"  # You can get the user's language here
    currency = "USD"  # You can get the user's currency here
    desc = "Premium subscription"  # You can get the description here

    client = AsyncAaioAPI(API_KEY, MERCHANT_KEY, MERCHANT_ID)
    URL = await client.create_payment(order_id, amount, lang, currency, desc)

    await callback_query.message.reply_text(f"Please pay for your premium subscription: {URL}")

    while True:
        if await client.is_expired(order_id):
            await callback_query.message.reply_text("Invoice was expired")
            break
        elif await client.is_success(order_id):
            await extend_premium_user_hrs(user_id, extend_hrs)
            await callback_query.message.reply_text("Payment was successful. Your premium subscription has been extended.")
            break
        else:
            await callback_query.message.reply_text("Invoice wasn't paid. Please pay the bill")
        await asyncio.sleep(5)