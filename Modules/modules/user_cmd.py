from pyrogram import filters
from helpers.helper import find_language
from helpers.filters import subscribed, user_registered
from langdb.rules import get_rules
from langdb.help_msg import get_help_msg

from Modules import cbot


# handle command /rules
@cbot.on_message(filters.command(["rules"]) & filters.private & subscribed & ~user_registered)
async def rules(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    if language:
        await message.reply(get_rules(language))


# handle command /help
@cbot.on_message(filters.command(["help"]) & filters.private & subscribed & ~user_registered)
async def help(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    if language:
        await message.reply(get_help_msg(language))