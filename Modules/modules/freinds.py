from pyrogram import filters
from pyrogram.errors import UserBlocked, UserIdInvalid, PeerIdInvalid, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

from database.premiumdb import save_premium_user, vip_users_details
from.. import cbot
import pyrostep
from helpers.helper import find_language
from helpers.forcesub import subscribed, user_registered
from helpers.translator import translate_async

pyrostep.listen(cbot)

button_pattern = re.compile(r"^(👫 (Friends|Друзья|Dostlar) 👫)$")

@cbot.on_message((filters.command("frens")| ((filters.regex(button_pattern))) & filters.private  & subscribed & user_registered))
async def frens(client, message):
    user_id = message.from_user.id
    language = find_language(user_id)
    frens_list = vip_users_details(user_id, "frens")
    keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(await translate_async("Add friend", language), callback_data="add_friend")]
        ])
    if frens_list:
        tr_txt = await translate_async("Here is the list of your friends:", language)
        frens_text = f"{tr_txt}\n\n"
        for friend_id in frens_list:
            detail = await client.get_users(friend_id)
            frens_text += f"{detail.mention}({friend_id})\n"
        await message.reply_text(frens_text, reply_markup=keyboard)
    else:
        tr_txt = f"f{await translate_async("You don't have any friends yet!", language)}\n\n{await translate_async("Add your friends now!", language)}"
        await message.reply_text(tr_txt, reply_markup=keyboard)

@cbot.on_callback_query(filters.regex("add_friend"))
async def add_friend(client, query):
    user_id = query.from_user.id
    language = find_language(user_id)
    await query.message.edit_text(await translate_async("Enter the ID of the friend you want to add:", language))
    friend_id_input = await pyrostep.wait_for(user_id)
    friend_id = friend_id_input.text
    frens_list = vip_users_details(user_id, "frens")

    if frens_list is not  None:
        for id in frens_list:
            if id == friend_id:
                query.message.reply_text(await translate_async("This user is already your friend.", language))
                return
    try:
        await client.get_users(friend_id)
    except UserIdInvalid:
        await query.message.reply_text(await translate_async("User ID invalid", language))
        return
    except:
        await query.message.reply_text(await translate_async("User not found in my database! Tell him to register first!", language))
        return
    if friend_id!= str(query.from_user.id):
        try:
            friend_id = friend_id
            try:
                detail = await client.get_users(user_id)
                await cbot.send_message(friend_id, f"{await translate_async("Friend request from")} {detail.mention}!\n\n {await translate_async("Do you want to add them as a friend?", language)}", reply_markup=InlineKeyboardMarkup([
                     [InlineKeyboardButton(await translate_async("Accept", language), callback_data=f"accept_friend_{user_id}"), InlineKeyboardButton(await translate_async("Decline", language), callback_data="decline_friend")]
                    ]))                
                await query.message.reply_text(await translate_async("Friend request sent successfully!", language))
            except UserBlocked:
                await query.message.reply_text(await translate_async("User has blocked the bot!", language))
            except RPCError as rc:
                await query.message.reply_text(await translate_async("Unable to send friend request! Please try again later.", language))
                print("rc:", rc)
        except ValueError:
            await query.message.reply_text(await translate_async("Invalid ID!", language))
        except Exception as e:
            await query.message.reply_text(f"{await translate_async("Unable to send friend request!\n\ne", language)} {e}")

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
    await query.message.reply_text(await translate_async("You have accepted the friend request!", language))
    detail = await client.get_users(user_id)
    await cbot.send_message(user_id, f"{detail.mention} {await translate_async("has accepted your friend request!")}")
    save_premium_user(user_id, frens=[friend_id])
    save_premium_user(friend_id, frens=[user_id])

@cbot.on_callback_query(filters.regex("decline_friend"))
async def decline_friend(client, query):
    language = find_language(query.from_user.id)
    await query.message.edit_text(await translate_async("You have declined the friend request!", language))