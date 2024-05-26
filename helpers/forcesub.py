from config import ADMINS as ADMIN_IDS
from Modules import BOT_ID
import os
import re
from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, ChatAdminRequired, PeerIdInvalid, UsernameNotOccupied, UsernameInvalid
from pyrogram.enums import ChatMemberStatus
from pyrogram.filters import Update
from helpers.helper import is_user_registered

async def is_subscribed(filter, client, update):
    promo_status = os.environ.get('PROMO_STATUS')
    if not promo_status or promo_status == "False":
        return True
    user_id = update.from_user.id
    if user_id in ADMIN_IDS:
        return True
    chat_ids = os.getenv("SUBSCRIPTION", "").split(",")
    if not chat_ids or chat_ids== [""]: # if the chat_ids list is empty
        return True
    
    for chat_id in chat_ids:
        if not await is_member(client, chat_id, user_id):
            return False
    
    return True

async def is_member(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
    except (PeerIdInvalid, ChatAdminRequired, UserNotParticipant, UsernameNotOccupied, UsernameInvalid): 
        return False
    if user_id == BOT_ID:
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return True
        return False
    if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return True
    return False  

subscribed = filters.create(is_subscribed)


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##


async def get_unjoined_channels(_, client, user_id):
    promo_status = os.environ.get('PROMO_STATUS')
    if not promo_status or promo_status == "False":
        return []
    if user_id in ADMIN_IDS:
        return []
    chat_ids = os.getenv("SUBSCRIPTION", "").split(",")
    if not chat_ids or chat_ids == [""]:  # if the chat_ids list is empty
        return []
    
    unjoined_channels = []
    for chat_id in chat_ids:
        if not await is_member(client, chat_id, user_id):
            unjoined_channels.append(chat_id)
    
    return unjoined_channels

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##


async def is_registered(filter, client, update: Update):
    user_id = update.from_user.id
    is_ok = is_user_registered(user_id)
    if is_ok:
        return True
    else:
        return False
    
user_registered = filters.create(is_registered)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

async def lens_2(filter, client, update):
    mesg = update.text    
    # Split the message into words
    words = mesg.split()
    # Check if the message has exactly two words and starts with "/start" followed by "a" and a number
    if len(words) == 2 and words[0] == "/start" and words[1].startswith("a"):
        return True
    return False

anoms_filter = filters.create(lens_2)