from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import urllib.parse


from zenova import zenova , BOT_USERNAME
from helpers.helper import find_language
from langdb.get_msg import get_premium_msg
from database.referdb import get_point


button_pattern = re.compile(r"^💎 (Premium|Премиум|Premium) 💎$")
@zenova.on_message(filters.private & filters.regex(button_pattern))
async def premium_option(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    caption, buttons = await get_premium_msg(language)
    await message.reply_text(caption, reply_markup=buttons)


@zenova.on_callback_query(filters.regex("^premium_free$"))
async def premium_free_callback(bot, update):
    # Your logic here to handle the callback query
    user_id = update.from_user.id
    total_points =await (get_point(user_id))
    # Assuming you have a function to generate the referral link
    referral_link = f"https://t.me/{BOT_USERNAME}?start=r{user_id}"
    share_txt = "Hey buddy!!\n\n Try this amazing bot for getting connected with strangers from the world!"
    encoded_share_txt = urllib.parse.quote(share_txt)
    share_link = f"https://t.me/share/url?url={referral_link}&text={encoded_share_txt}"
    print("share link:", share_link)
    await update.message.edit_text(
        text=f"Invite users using your link and receive 👑VIP status for 1 hour for each!\n\nInvited:{total_points} \n\nYour personal link:\n👉 {referral_link}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Refer your Friend", url= share_link)]]
        )
    )