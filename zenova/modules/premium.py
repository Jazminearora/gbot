from pyrogram import filters
import re
from zenova import zenova 


button_pattern = re.compile(r"^💎 (Premium|Премиум|Premium) 💎$")
@zenova.on_message(filters.private & filters.regex(button_pattern))
async def premium_option(client, message):
    await message.reply_text("You selected Premium option.")