from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import urllib.parse


from Modules import cbot , BOT_USERNAME
from helpers.helper import find_language
from langdb.get_msg import get_premium_msg
from database.referdb import get_point
from helpers.forcesub import subscribed, user_registered


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
    await handle_premium_free_request(update)

@cbot.on_callback_query(filters.regex("^premium_free$") & subscribed & user_registered)
async def premium_free_callback(bot, update):
    await handle_premium_free_request(update)
