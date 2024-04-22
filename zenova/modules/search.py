from pyrogram import filters
import re
from zenova import zenova 


button_pattern = re.compile(r"^(🔍 (Search for an interlocutor|Найти собеседника|Məqalə axtar) 🔎$")


@zenova.on_message(filters.private & filters.regex(button_pattern))
async def search_interlocutor(client, message):
    await message.reply_text("Searching for an interlocutor...")