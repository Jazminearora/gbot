from config import ADMINS
from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.enums import ChatMemberStatus

chat_ids = (-1001685809766, -1002104201071)

async def is_subscribed(filter, client, update):
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    
    if not is_member(client, chat_ids[0], user_id) or not is_member(client, chat_ids[1], user_id):
        return False
    
    return True

async def is_member(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
    except UserNotParticipant:
        return False
    if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return True
    return False  

subscribed = filters.create(is_subscribed)