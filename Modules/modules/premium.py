from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import urllib.parse


from Modules import cbot , BOT_USERNAME
from helpers.helper import find_language
from helpers.translator import translate_text
from langdb.get_msg import get_premium_msg
from database.referdb import get_point
from helpers.forcesub import subscribed, user_registered

async def get_text(total_points, referral_link, language)
    msg=f"Invite users using your link and receive 👑VIP status for 1 hour for each!\n\nInvited:"
    msg2 =f"Your personal link:\n👉"
    translations = {"English": msg, "Russian": translate_text(msg, target_language="ru"), "Azerbejani": translate_text(msg, target_language="az")}
    translations = {"English": msg2, "Russian": translate_text(msg2, target_language="ru"), "Azerbejani": translate_text(msg2, target_language="az")}
    message =  translations.get(language, msg) + total_points + f"\n\n" + translations.get(language, msg2) + referral_link
    return message

button_pattern = re.compile(r"^💎 (Premium|Премиум|Premium) 💎$")
@cbot.on_message(filters.private & filters.regex(button_pattern))
async def premium_option(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    caption, buttons = await get_premium_msg(language)
    await message.reply_text(caption, reply_markup=buttons)


async def handle_premium_free_request(update):
    user_id = update.from_user.id
    total_points = await get_point(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start=r{user_id}"
    share_txt = "Hey buddy!!\n\n Try this amazing bot for getting connected with strangers from the world!"
    encoded_share_txt = urllib.parse.quote(share_txt)
    share_link = f"https://t.me/share/url?url={referral_link}&text={encoded_share_txt}"
    print("share link:", share_link)
    await update.message.reply_text(
        text=f"Invite users using your link and receive 👑VIP status for 1 hour for each!\n\nInvited:{total_points} \n\nYour personal link:\n👉 {referral_link}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refer your Friend", url=share_link)]]
        )
    )

@cbot.on_message(filters.command("referals") & subscribed & user_registered)
async def premium_free_command_handler(bot, update):
    user_id = update.from_user.id
    user_lang = find_language(user_id)
    total_points = await get_point(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start=r{user_id}"
    share_txt = "Hey buddy!!\n\n Try this amazing bot for getting connected with strangers from the world!"
    encoded_share_txt = urllib.parse.quote(share_txt)
    share_link = f"https://t.me/share/url?url={referral_link}&text={encoded_share_txt}"
    print("share link:", share_link)
    message = await get_text(total_points, referral_link, user_lang)
    await update.reply_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refer your Friend", url=share_link)]]
        )
    )

@cbot.on_callback_query(filters.regex("^premium_free$") & subscribed & user_registered)
async def premium_free_callback(bot, update):
    await handle_premium_free_request(update)
