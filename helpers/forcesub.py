from config import ADMINS as ADMIN_IDS
from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.enums import ChatMemberStatus
from helpers.helper import is_user_registered

chat_ids = [-1001997140154, -1001943241575]

async def is_subscribed(filter, client, update):
    user_id = update.from_user.id
    if user_id in ADMIN_IDS:
        return True
    
    if not chat_ids: # if the chat_ids list is empty
        return True
    
    for chat_id in chat_ids:
        if not await is_member(client, chat_id, user_id):
            return False
    
    return True

async def is_member(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
    except UserNotParticipant:
        return False
    if member. status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return True
    return False  

subscribed = filters.create(is_subscribed)


##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##


async def is_registered(filter, client, update):
    user_id = update.from_user.id
    is_ok = is_user_registered(user_id)
    if is_ok:
        return True
    else:
        return False
    
user_registered = filters.create(is_registered)
