import re
from Modules import cbot
from pyrogram import filters
from Modules import cbot
from helpers.forcesub import subscribed, user_registered



button_pattern = re.compile(r"^(🔧 (Configure search|Настроить поиск|Axtarışı tənzimlə) 🔧)$")


@cbot.on_message(((filters.private & filters.regex(button_pattern)) | (filters.command("configure"))) & subscribed & user_registered)
async def configure_search(client, message):
    await message.reply_text("ok brthr")