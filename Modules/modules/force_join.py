import os
from Modules import cbot, BOT_USERNAME
from helpers.forcesub import subscribed
from config import FORCE_MSG
from pyrogram import filters
from ..modules.admin import get_chat_ids
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


@cbot.on_message(filters.command("start") & filters.private & ~subscribed)
async def not_joined(client, message: Message):
    buttons = []
    chat_ids = get_chat_ids()
    for chat_id in chat_ids:
        try:
            print("sz", chat_id)
            chat = await cbot.get_chat(chat_id)
            print(chat)
            invite_link = await chat.invite_link
            buttons.append(
                [InlineKeyboardButton(text=chat.title, url=invite_link)]
            )
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
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Continue",
                    url=f"https://t.me/{BOT_USERNAME}?start"
                )
            ]
        )
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