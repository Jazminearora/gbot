from zenova import zenova, BOT_USERNAME
from helpers.forcesub import subscribed
from config import FORCE_MSG
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@zenova.on_message(filters.command('start') & filters.private & ~subscribed)
async def not_joined(client, message):
    buttons = [
        [
            InlineKeyboardButton(text="Join Channel", url="t.me/about_xytra"),
            InlineKeyboardButton(text="Join Channel", url="t.me/zenova_prime"),
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text = 'Try Again',
                    url = f"https://t.me/{BOT_USERNAME}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await message.reply(
        text = FORCE_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
        reply_markup = InlineKeyboardMarkup(buttons),
        quote = True,
        disable_web_page_preview = True
    )