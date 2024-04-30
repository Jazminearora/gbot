import re
from pyrogram.errors import PeerIdInvalid
from pyrogram.enums import ParseMode
from pyrogram import filters

from .. import cbot
from helpers.forcesub import subscribed, user_registered
from helpers.helper import find_language
from database.referdb import get_top_referers
from langdb.get_msg import get_top_text, get_points_text, get_prize_text, get_no_referers_text

button_pattern = re.compile(r"^(🔝 (Top|Лучшие|Ən yuxarı) 🔝)$")

@cbot.on_message((filters.command("top")| ((filters.regex(button_pattern))) & filters.private  & subscribed & user_registered))
async def frens(client, message):
    lang = find_language(message.from_user.id)
    top_referers = await get_top_referers()
    if top_referers:
        # Create a list of strings to store the top referers with their points
        top_referers_str = []
        # Iterate over the top referers and append their IDs and points to the list
        for i, (referer_id, points) in enumerate(top_referers, start=1):
            print(referer_id, points)
            if i <= 5:
                try:
                    meter = await client.get_users(referer_id)
                    mention = meter.mention(style="html")
                except PeerIdInvalid:
                    mention = referer_id
                top_referers_str.append(f"{i}. {mention} - {points} {get_points_text(lang)}")
        # Create a string to display the top referers
        top_referers_text = "\n".join(top_referers_str)
        # Send a message to the user with the top referers
        await message.reply(f"<b>{get_top_text(lang)}:</b>\n\n{top_referers_text}\n\n<b>{get_prize_text(lang)}</b>", parse_mode=ParseMode.HTML)
    else:
        # Send a message to the user if there are no top referers
        await message.reply(get_no_referers_text(lang), parse_mode=ParseMode.HTML)