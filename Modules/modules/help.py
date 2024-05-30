from pyrogram import filters
from helpers.helper import find_language
from helpers.filters import subscribed
from langdb.rules import get_rules
from langdb.help_msg import get_help_msg

from Modules import cbot


# handle command /rules
@cbot.on_message(filters.command(["rules"]) & filters.private )
async def rules(client, message):
    print("vd ho")
    user_id = message.from_user.id
    language = find_language(user_id)
    if language:
        await message.reply(get_rules(language))


# handle command /help
@cbot.on_message(filters.command(["help"]) & filters.private)
async def help(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    if language:
        await message.reply(get_help_msg(language))