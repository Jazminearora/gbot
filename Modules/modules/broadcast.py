import os
from pyrogram import filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
import datetime, time
import pyrostep

from helpers.helper import get_users_list
from Modules import cbot, logger

pyrostep.listen(cbot)

broadcasting_in_progress = False
failed_users = []
preview_mode = False

@cbot.on_callback_query(filters.regex(r'^newsletter$'))
async def newsletter_handler(_, query):


    global preview_mode


    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Preview Mode On", callback_data='preview_on'),
            InlineKeyboardButton("Preview Mode Off", callback_data='preview_off'),
        ]
    ])
    await query.message.reply_text(f'Preview mode: {preview_mode}\n\nPlease choose a preview mode:', reply_markup=reply_markup)

@cbot.on_callback_query(filters.regex(r'^preview_(on|off)$'))
async def preview_handler(_, query):
    global preview_mode
    if query.data == 'preview_on':
        preview_mode = True
    else:
        preview_mode = False
    lang_buttons = [
        [
            InlineKeyboardButton("English", callback_data='newsletter_English'),
            InlineKeyboardButton("Russian", callback_data='newsletter_Russian'),
            InlineKeyboardButton("Azerbejani", callback_data='newsletter_Azerbejani'),
        ],
        [
            InlineKeyboardButton("Cancel", callback_data='cancel')
        ]
    ]
    lang_markup = InlineKeyboardMarkup(lang_buttons)
    await query.message.reply_text(text="Please choose the language for the newsletter recipients:", reply_markup=lang_markup)


async def wait_for_10_seconds():
    await asyncio.sleep(10)
    return True

@cbot.on_callback_query(filters.regex(r'^newsletter_(English|Russian|Azerbejani)$'))
async def newsletter_language_handler(_, query):
    lang = query.data.split('_')[1]
    await query.message.edit_text(text="Enter the newsletter message:")
    newsletter_msg = await pyrostep.wait_for(query.from_user.id)
    if newsletter_msg:
        if preview_mode:
            await newsletter_msg.forward(chat_id=int(query.from_user.id))
        else:
            await newsletter_msg.copy(chat_id=int(query.from_user.id))
        await cbot.send_message(query.from_user.id, text="Do you want to broadcast this message? (y/n)")
        confirmation = await pyrostep.wait_for(query.from_user.id)
        confirmation_text = confirmation.text
        if confirmation_text == 'y':
            global broadcasting_in_progress
            broadcasting_in_progress = True
            users = get_users_list(lang)
            stop_broadcast_button = InlineKeyboardButton("Stop Broadcasting", callback_data="stop_broadcast")
            stop_broadcast_markup = InlineKeyboardMarkup([[stop_broadcast_button]])
            sts_msg = await cbot.send_message(query.from_user.id, text="Starting process of Sending newsletter in 10 seconds...", reply_markup=stop_broadcast_markup)

            # Wait for 10 seconds
            if await wait_for_10_seconds():
                done = 0
                failed = 0
                success = 0
                start_time = time.time()
                total_users = len(users)
                for user in users:
                    if broadcasting_in_progress:
                        sts = await send_newsletter(user, newsletter_msg)
                        if sts == 200:
                            success += 1
                        else:
                            failed += 1
                        done += 1
                        if not done % 20:
                            await sts_msg.edit(
                                text=f"Sending newsletter...\nTotal users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}"
                            )
                    else:
                        break

                if broadcasting_in_progress:
                    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
                    await cbot.send_message(query.from_user.id,
                        text=f"Newsletter sent successfully!\nCompleted in {completed_in}\nTotal users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}"
                    )
                else:
                    await cbot.send_message(query.from_user.id, text="Broadcasting stopped by admin.")
            else:
                await cbot.send_message(query.from_user.id, text="Broadcasting cancelled by admin.")
        elif confirmation_text == 'n':
            await cbot.send_message(query.from_user.id, text="Broadcast cancelled by admin.")
        else:
            await cbot.send_message(query.from_user.id, text="Invalid response. Please enter y or n.")
    else:
        await cbot.send_message(query.from_user.id, text="Newsletter message not received. Please try again.")
@cbot.on_callback_query(filters.regex(r'^stop_broadcast$'))
async def stop_broadcasting_handler(_, query):
    global broadcasting_in_progress
    broadcasting_in_progress = False
    await query.message.edit_text(text="Broadcasting stopped.")

async def send_newsletter(user_id, message):
    global preview_mode
    try:
        if preview_mode:
            await message.forward(chat_id=int(user_id))
        else:
            await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return send_newsletter(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Deactivated")
        failed_users.append(user_id)
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Blocked")
        failed_users.append(user_id)
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Invalid ID")
        failed_users.append(user_id)
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        failed_users.append(user_id)
        return 500