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
    top_users, user_position, user_chat_time = get_top_chat_users(message.from_user.id)
    print(get_top_chat_users(message.from_user.id))

    # Format the chat time for the users
    formatted_top_users = []
    for user in top_users:
        formatted_chat_time = str(timedelta(seconds=user["chat_time"]))
        formatted_top_users.append(f"{user['user_id']} - in dialogues {formatted_chat_time}")

    # Create the message
    message_text = (
        "🏆 **Spend more time in dialogues than others and get a prize - a subscription 💎 PREMIUM**\n\n"
        "📅 **Everyone takes part automatically, the drawing period is every week from Monday to Sunday**\n\n"
        "⏳ **Summing up and distribution of prizes every Sunday at 20:00 Moscow time.**\n\n"
        "🏆 **Prizes:**\n"
        "🥇 **1st place** - free subscription for 3 days\n"
        "🥈 **2nd place** - free subscription for 2 days\n"
        "🥉 **3rd place** - free subscription for 1 day\n\n"
        "📊 **Current leaders:**\n"
    )

    # Add the top users to the message
    for i, user in enumerate(formatted_top_users):
        message_text += f"{i + 1}. {user}\n"

    # Add the user's position to the message
    if user_chat_time == 0:
        message_text += "\n👤 **Your position:**\n"
        message_text += "📵🚭🔇 - in dialogues 20s"
    else:
        message_text += f"\n👤 **Your position:**\n"
        try:
            timee = str(timedelta(seconds=user_chat_time))
        except Exception:
            timee = 0
        message_text += f"{user_position}. {message.from_user.id} - in dialogues {timee}"

    message_text += "\n\n❕ **Time farming is prohibited, and accounts with a suspiciously low number of dialogues and sent messages will be blocked in our bot and removed from the TOP.**"

    # Send the message
    await client.send_message(
        chat_id=message.chat.id,
        text=message_text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
    )


















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