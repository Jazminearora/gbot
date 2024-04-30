import re
from pyrogram.errors import PeerIdInvalid
from pyrogram.enums import ParseMode
from pyrogram import filters
from datetime import timedelta

from Modules import cbot
from helpers.forcesub import subscribed, user_registered
from helpers.helper import find_language
from database.referdb import get_top_referers
from database.premiumdb import get_top_chat_users
from langdb.get_msg import get_top_text, get_points_text, get_prize_text, get_no_referers_text

button_pattern = re.compile(r"^(🔝 (Top|Лучшие|Ən yuxarı) 🔝)$")

@cbot.on_message((filters.command("top")| ((filters.regex(button_pattern))) & filters.private  & subscribed & user_registered))
async def frens(client, message):
    # Get the top chat users
    top_users = await get_top_chat_users()

    # Get the user's position and chat time
    user_position = 0
    user_chat_time = 0
    for i, user in enumerate(top_users):
        if user["user_id"] == message.from_user.id:
            user_position = i + 1
            user_chat_time = user["chat_time"]

    # Format the chat time
    formatted_user_chat_time = str(timedelta(seconds=user_chat_time))

    # Prepare the message
    msg = f"<b>Spend more time in dialogues than others and get a prize - a subscription 💎 PREMIUM</b>\n\n"
    msg += "Everyone takes part automatically, the drawing period is every week from Monday to Sunday\n"
    msg += "Summing up and distribution of prizes every Sunday at 20:00 Moscow time.\n\n"
    msg += "Prizes:\n"
    msg += "🥇1st place - free subscription for 3 days\n"
    msg += "🥈2nd place - free subscription for 2 days\n"
    msg += "🥉3rd place - free subscription for 1 day\n\n"
    msg += "Current leaders:\n"

    # Add the top users to the message
    for i, user in enumerate(top_users):
        if i < 3:
            formatted_user_chat_time = str(timedelta(seconds=user["chat_time"]))
            msg += f"{i+1}. {user['user_id']} - in dialogues {formatted_user_chat_time}\n"
        else:
            break

    # Add the user's position to the message
    if user_position == 0:
        msg += "Your position:\n"
    else:
        msg += f"Your position:\n{user_position}. {message.from_user.first_name} - in dialogues {formatted_user_chat_time}\n"

    msg += "\n❕ Time farming is prohibited, and accounts with a suspiciously low number of dialogues and sent messages will be blocked in our bot and removed from the TOP."

    # Send the message
    await message.reply_text(msg, parse_mode=ParseMode.HTML)



















# async def frens(client, message):
#     lang = find_language(message.from_user.id)
#     top_referers = await get_top_referers()
#     if top_referers:
#         # Create a list of strings to store the top referers with their points
#         top_referers_str = []
#         # Iterate over the top referers and append their IDs and points to the list
#         for i, (referer_id, points) in enumerate(top_referers, start=1):
#             print(referer_id, points)
#             if i <= 5:
#                 try:
#                     meter = await client.get_users(referer_id)
#                     mention = meter.mention(style="html")
#                 except PeerIdInvalid:
#                     mention = referer_id
#                 top_referers_str.append(f"{i}. {mention} - {points} {get_points_text(lang)}")
#         # Create a string to display the top referers
#         top_referers_text = "\n".join(top_referers_str)
#         # Send a message to the user with the top referers
#         await message.reply(f"<b>{get_top_text(lang)}:</b>\n\n{top_referers_text}\n\n<b>{get_prize_text(lang)}</b>", parse_mode=ParseMode.HTML)
#     else:
#         # Send a message to the user if there are no top referers
#         await message.reply(get_no_referers_text(lang), parse_mode=ParseMode.HTML)