from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
import re
import pyrostep

from.. import cbot
from database.premiumdb import save_premium_user, vip_users_details, remove_item_from_field
from helpers.helper import get_profile
from helpers.helper import find_language
from helpers.forcesub import subscribed, user_registered
from helpers.translator import translate_async
from Modules.modules.register import get_user_name
from Modules.modules.new_search import is_chatting, is_user_searching #, add_pair

pyrostep.listen(cbot)

button_pattern = re.compile(r"^(👫 (Friends|Друзья|Dostlar) 👫)$")

@cbot.on_message((filters.command("frens")| ((filters.regex(button_pattern))) & filters.private  & subscribed & user_registered))
async def frens(_, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    frens_list = vip_users_details(user_id, "frens")

    if not frens_list:
        tr_txt = await translate_async("You don't have any friends yet! Make some friends during chats!", language)
        await message.reply_text(tr_txt)
    else:
        tr_txt = await translate_async("Here are your friends:", language)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{await get_user_name(friend_id)}", callback_data=f"fren_{friend_id}")]
            for friend_id in frens_list
        ])
        await message.reply_text(tr_txt, reply_markup=keyboard)


@cbot.on_callback_query(filters.regex("accept_friend_"))
async def accept_friend(client, query):
    user_id = int(query.data.split("_")[2])
    language = find_language(user_id)
    friend_id = query.from_user.id
    frens_list = vip_users_details(user_id, "frens")
    if frens_list is not  None:
        for id in frens_list:
            if id == friend_id:
                query.message.reply_text(await translate_async("This user is already your friend.", language))
                return   
    await query.message.edit_text(await translate_async("You have accepted the friend request!", language))
    detail = await client.get_users(friend_id)
    await cbot.send_message(user_id, f"{detail.mention} {await translate_async("has accepted your friend request!", language)}")
    save_premium_user(user_id, frens=[friend_id])
    save_premium_user(friend_id, frens=[user_id])

@cbot.on_callback_query(filters.regex("decline_friend"))
async def decline_friend(client, query):
    language = find_language(query.from_user.id)
    await query.message.edit_text(await translate_async("You have declined the friend request!", language))


#```````````````````````````````````````````````````````````````````````````````````````````````````````````````````#
#```````````````````````````````````````````````````````````````````````````````````````````````````````````````````#

@cbot.on_callback_query(filters.regex(r"fren_(\d+)"))
async def friend_profile(client, callback_query):
    user_id = int(callback_query.data.split("_")[1])
    language = find_language(callback_query.from_user.id)
    profile_raw, _ = await get_profile(user_id, language, "user_profile")

    # Remove the line containing "?start=r"
    profile_text = '\n'.join([line for line in profile_raw.split('\n') if "?start=r" not in line])

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(await translate_async("📞 Request chat", language), callback_data=f"request_chat_{user_id}"),
            InlineKeyboardButton(await translate_async(" 💔 Unfriend", language), callback_data=f"unfriend_{user_id}"),
        ],
        [
            InlineKeyboardButton(await translate_async("🔙 Back", language), callback_data="back_frens"),
        ]
    ])

    await callback_query.message.edit_text(profile_text, reply_markup=keyboard)


#```````````````````````````````````````````````````````````````````````````````````````````````````````````````````#
#```````````````````````````````````````````````````````````````````````````````````````````````````````````````````#


@cbot.on_callback_query(filters.regex(r"back_frens"))
async def back_frens(_, callback_query):
    user_id = callback_query.from_user.id
    language = find_language(user_id)
    frens_list = vip_users_details(user_id, "frens")

    if not frens_list:
        tr_txt = await translate_async("You don't have any friends yet! Make some friends during chats!", language)
        await callback_query.message.edit_text(tr_txt)
    else:
        tr_txt = await translate_async("Here are your friends:", language)
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"{await get_user_name(friend_id)}", callback_data=f"fren_{friend_id}")
            ]
            for friend_id in frens_list
        ])
        await callback_query.message.edit_text(tr_txt, reply_markup=keyboard)


#```````````````````````````````````````````````````````````````````````````````````````````````````````````````````#
#```````````````````````````````````````````````````````````````````````````````````````````````````````````````````#


@cbot.on_callback_query(filters.regex(r"unfriend_(\d+)"))
async def unfriend_callback(_, callback_query):
    user_id = int(callback_query.from_user.id)
    language = find_language(user_id)
    friend_id = int(callback_query.data.split("_")[1])
    frens_list = vip_users_details(user_id, "frens")
    if frens_list is None or friend_id not in frens_list:
        await callback_query.answer(await translate_async("This user is not your friend.", language), show_alert=True)
        return
    confirm_text = await translate_async("Are you sure, you want to unfriend {}?", language)
    
    reply_markup= InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Yes", callback_data=f"unfriend_confirm_{friend_id}"),
                    InlineKeyboardButton("No", callback_data="unfriend_cancel"),
                ]
            ]
        )

    await callback_query.message.edit_text(confirm_text.format(friend_id), reply_markup= reply_markup)

@cbot.on_callback_query(filters.regex("unfriend_confirm_"))
async def unfriend_confirm(client, query):
    friend_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    language = find_language(user_id)
    await query.message.edit_text(await translate_async("You have unfriended the user!", language))
    remove_item_from_field(user_id, "frens", friend_id)
    remove_item_from_field(friend_id, "frens", user_id)
    await cbot.send_message(friend_id, await translate_async("You have been unfriended by your one of friend!", language))


@cbot.on_callback_query(filters.regex("unfriend_cancel"))
async def unfriend_cancel(client, query):
    await query.message.edit_text(await translate_async("Unfriend action cancelled.", query.from_user.id))


#```````````````````````````````````````````````````````````````````````````````````````````````````````````````````#
#```````````````````````````````````````````````````````````````````````````````````````````````````````````````````#


# @cbot.on_callback_query(filters.regex(r"request_chat_(\d+)"))
# async def request_chat_callback(_, callback_query: CallbackQuery):
#     friend_id = int(callback_query.data.split("_")[1])
#     user_id = callback_query.from_user.id
#     user_name = await get_user_name(user_id)
#     user_language = find_language(user_id)
#     friend_language = find_language(friend_id)

#     if await is_chatting(user_id, callback_query.message, user_language):
#         keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("End chat", user_language))]], resize_keyboard=True, one_time_keyboard=True)
#         tr_txt = await translate_async("You are already in a chat. End the chat first by using below button!", user_language)
#         await callback_query.message.reply(tr_txt, reply_markup= keyboard)
#         return

#     if await is_user_searching(user_id):
#         keyboard = ReplyKeyboardMarkup([[KeyboardButton(await translate_async("Stop Searching", user_language))]], resize_keyboard=True, one_time_keyboard=True)
#         tr_txt = await translate_async("You are already searching. Stop searching first by using below button!", user_language)
#         await callback_query.message.reply(tr_txt,  reply_markup= keyboard)
#         return
    
#     if await is_user_searching(friend_id):
#         tr_txt = await translate_async("You friend is already searching for anyone!", user_language)
#         await callback_query.message.reply(tr_txt,  reply_markup= keyboard)
#         return

#     if await is_chatting(friend_id, callback_query.message, friend_language):
#         tr_txt = await translate_async("Your friend is already chatting with someone!", user_language)
#         await callback_query.message.reply(tr_txt,  reply_markup= keyboard)
#         return
#     try:
#         tr_txt = await translate_async("Your friend {} wants to chat with you. Do you want to chat with him?", friend_language)
#         keyboard = [[InlineKeyboardButton(translate_async("Yes, start chat!", friend_language), callback_data=f"accept_chat_{user_id}"), 
#                     InlineKeyboardButton(translate_async("No, not now!", friend_language), callback_data=f"decline_chat_{user_id}")]]
#         await cbot.send_message(friend_id, tr_txt.format(user_name), reply_markup=InlineKeyboardMarkup(keyboard))
#     except Exception as e:
#         print(f"An exception occured while sending chat request to a friend: {e}")
#         await callback_query.message.reply(f"{translate_async("Failed to send chat request.", user_language)}")

# @cbot.on_callback_query(filters.regex(r"accept_chat_(\d+)"))
# async def accept_chat_callback(client, callback_query):
#     user_id = int(callback_query.data.split("_")[1])
#     add_pair(user_id, callback_query.from_user.id)
#     tr_txt = await translate_async("Chat started!", callback_query.from_user.language)
#     await callback_query.message.edit_text(tr_txt)

# @cbot.on_callback_query(filters.regex(r"decline_chat_(\d+)"))
# async def decline_chat_callback(client, callback_query):
#     user_id = int(callback_query.data.split("_")[1])
#     tr_txt = await translate_async("Chat request declined.", callback_query.from_user.language)
#     await callback_query.message.edit_text(tr_txt)