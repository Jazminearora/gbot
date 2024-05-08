import pyrogram
from pyrogram import filters, types

from database.premiumdb import is_user_premium
from helpers.helper import find_language
from helpers.forcesub import user_registered, subscribed
from .. import cbot

# @cbot.on_message(user_registered, subscribed)
# async def advert_user(_, message)