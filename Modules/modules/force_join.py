import os
from Modules import cbot, BOT_USERNAME, LOG_GROUP
from helpers.forcesub import subscribed, user_registered, is_subscribed
from pyrogram import filters
from ..modules.subscription import get_chat_ids
from helpers.translator import translate_async
from helpers.helper import find_language
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery


@cbot.on_message(filters.command("start") & filters.private & ~subscribed & user_registered)
async def not_joined(client, message: Message):
    buttons = []
    chat_ids_str = get_chat_ids()
    chat_ids = [int(chat_id) for chat_id in chat_ids_str.split(",")]
    for chat_id in chat_ids:
        try:
            chat = await cbot.get_chat(chat_id)
            invite_link = await get_invite_link(chat_id)
            if invite_link is not None:
                buttons.append(
                [InlineKeyboardButton(text=chat.title, url=invite_link)]
            )
        except Exception as e:
            print(f"Error getting invite link for chat {chat_id}: {e}")

    lang = find_language(message.from_user.id)
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=await translate_async("Continue", lang),
                    url=f"https://t.me/{BOT_USERNAME}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=await translate_async("Continue", lang),
                    callback_data="refresh_status"
                )
            ]
        )
        pass

    text = await translate_async("Please join our all the channels below first to continue.", lang)
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))

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

@cbot.on_callback_query(filters.regex("refresh_status"))
async def refresh_status_callback(client, query: CallbackQuery):
    if not await is_subscribed("_", client, query.message):
        await query.answer(await translate_async("Your status has been updated. You can now continue using the bot."))
        await query.message.delete()
    else:
        await query.answer("Your account is still banned. Please try again later.")