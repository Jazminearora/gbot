import os
from Modules import cbot, BOT_USERNAME, LOG_GROUP
from helpers.forcesub import subscribed
from config import FORCE_MSG
from pyrogram import filters
from ..modules.admin import get_chat_ids
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


@cbot.on_message(filters.command("start") & filters.private & ~subscribed)
async def not_joined(client, message: Message):
    buttons = []
    chat_ids_str = get_chat_ids()
    chat_ids = [int(chat_id) for chat_id in chat_ids_str.split(",")]
    for chat_id in chat_ids:
        try:
            chat = await cbot.get_chat(chat_id)
            invite_link = await get_invite_link(chat_id)
            print(invite_link)
            if invite_link is not None:
                buttons.append(
                [InlineKeyboardButton(text=chat.title, url=invite_link)]
            )
            else:
                print("none 1")
        except Exception as e:
            print(f"Error getting invite link for chat {chat_id}: {e}")

    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Continue",
                    url=f"https://t.me/{BOT_USERNAME}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else "@" + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )

async def get_invite_link(chat_id):
    try:
        chat = await cbot.get_chat(chat_id)
        if chat.invite_link:
            link = chat.invite_link
            return link
        if chat.username and not chat.invite_link:
            link = f"https://t.me/{chat.username}"
            return link
        try:
            if not chat.invite_link and not chat.username:
                link = await cbot.export_chat_invite_link(chat_id)
                return link
        except Exception as e:
            print(f"Error while creating invite link for chat {chat_id}: {e}")
            await cbot.send_message(LOG_GROUP, "Error while creating invite link for chat {chat_id}: {e}")
            return None
    except Exception as e:
        print(f"Error getting invite link for chat {chat_id}: {e}")
        await cbot.send_message(LOG_GROUP, "Error getting invite link for chat {chat_id}: {e}")
    await cbot.send_message(LOG_GROUP, f"Could not generate invite link for chat ID {chat_id}")
    return None