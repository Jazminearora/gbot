from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import urllib.parse

from helpers.helper import find_language
from helpers.translator import translate_async
from Modules import cbot , BOT_USERNAME
from langdb.get_msg import get_premium_msg
from database.referdb import get_point

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

@cbot.on_callback_query(filters.regex("^premium_free$"))
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