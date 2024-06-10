from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import re
import pyrostep

from.. import cbot 
from database.premiumdb import save_premium_user, vip_users_details, remove_item_from_field
from helpers.helper import get_profile
from helpers.helper import find_language
from helpers.filters import subscribed, user_registered
from helpers.translator import translate_async

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
                    [InlineKeyboardButton(friend["nickname"], callback_data=f"fren_{friend['friend_id']}")]
                    for friend in frens_list
                ])
        await message.reply_text(tr_txt, reply_markup=keyboard)


@cbot.on_callback_query(filters.regex("accept_friend_"))
async def accept_friend(client, query):
    user_id = int(query.data.split("_")[2])
    nickname1= str(query.data.split("_")[3])
    language = find_language(user_id)
    friend_id = query.from_user.id
    frens_list = vip_users_details(user_id, "frens")
    if frens_list is not None and isinstance(frens_list, list):
        for friend_id in frens_list:
            if friend_id["friend_id"] == friend_id:
                await query.message.reply_text(await translate_async("This user is already your friend.", language))
                return
    await query.message.reply_text(await translate_async("Enter a nickname for your friend:", language))
    try: 
        uu = await pyrostep.wait_for(friend_id, timeout = 40)
        nickname2 = uu.text
    except TimeoutError:
        await query.message.reply_text(await translate_async("No nickname received!!", language))
        return 
    await query.message.edit_text(await translate_async("You have accepted the friend request!", language))
    await cbot.send_message(user_id, f"{nickname1} {await translate_async("has accepted your friend request!", language)}")
    save_premium_user(user_id, frens={'friend_id': friend_id, "nickname": nickname1})
    save_premium_user(friend_id, frens={'friend_id': user_id, "nickname": nickname2})

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
    frens_list = vip_users_details(callback_query.from_user.id, "frens")
    for friend in frens_list:
        if friend['friend_id'] == int(user_id):
            nickname = friend["nickname"]
            break
    profile_raw, _ = await get_profile(user_id, language, "user_profile", name= nickname)

    # Remove the line containing "?start=r"
    profile_text = '\n'.join([line for line in profile_raw.split('\n') if "?start=" not in line])

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(await translate_async("📞 Request chat", language), callback_data=f"request_chat_{user_id}"),
            InlineKeyboardButton(await translate_async(" 💔 Unfriend", language), callback_data=f"unfriend_{user_id}"),
        ],
        [
            InlineKeyboardButton(await translate_async("🪬 Gift premium", language), callback_data=f"gift_fren_{user_id}"),
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
                    [InlineKeyboardButton(friend["nickname"], callback_data=f"fren_{friend['friend_id']}")]
                    for friend in frens_list
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
    if frens_list is None or all(friend["friend_id"]!= friend_id for friend in frens_list):
        await callback_query.answer(await translate_async("This user is not your friend.", language), show_alert=True)
        return
    confirm_text = await translate_async("Are you sure, you want to unfriend him?", language)
    
    reply_markup= InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(await translate_async("Yes 💔", language), callback_data=f"unfriend_confirm_{friend_id}"),
                    InlineKeyboardButton(await translate_async("No ❤️", language), callback_data="unfriend_cancel"),
                ]
            ]
        )

    await callback_query.message.edit_text(confirm_text, reply_markup= reply_markup)

@cbot.on_callback_query(filters.regex("unfriend_confirm_"))
async def unfriend_confirm(client, query):
    friend_id = int(query.data.split("_")[2])
    user_id = query.from_user.id
    language = find_language(user_id)
    frens_list1 = vip_users_details(user_id, "frens")
    for friend in frens_list1:
        if friend["friend_id"] == friend_id:
            name1 = friend["nickname"]
    frens_list2 = vip_users_details(friend_id, "frens")
    for friend in frens_list2:
        if friend["friend_id"] == user_id:
            name2 = friend["nickname"]
    await query.message.edit_text(f"{await translate_async(f"You have unfriended", language)} {name1}!")
    remove_item_from_field(user_id, "frens", {"friend_id": friend_id, "nickname": name1})
    remove_item_from_field(friend_id, "frens", {"friend_id": user_id, "nickname": name2})
    await cbot.send_message(friend_id, f"{await translate_async("You have been unfriended by", language)} {name2}!")


@cbot.on_callback_query(filters.regex("unfriend_cancel"))
async def unfriend_cancel(client, query):
    await query.message.edit_text(await translate_async("Unfriend action cancelled.", query.from_user.id))


"""
The code for send chat request, accept chat request and start a dialoge is defined in new_search.py file from line 760 to 830
"""