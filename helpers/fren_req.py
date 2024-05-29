from pyrogram.errors import UserBlocked, UserIdInvalid, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.premiumdb import vip_users_details
from Modules import cbot
from helpers.translator import translate_async



async def process_friend_request(client, message, user_id, friend_id, language):
    frens_list = vip_users_details(user_id, "frens")

    if frens_list is not None:
        for id in frens_list:
            if id == friend_id:
                await message.reply_text(await translate_async("This user is already your friend.", language))
                return
    try:
        await client.get_users(friend_id)
    except UserIdInvalid:
        await message.reply_text(await translate_async("User ID invalid", language))
        return
    except:
        await message.reply_text(await translate_async("User not found in my database! Tell him to register first!", language))
        return
    
    if friend_id != str(message.from_user.id):
        try:
            friend_id = friend_id
            try:
                detail = await client.get_users(user_id)
                await cbot.send_message(friend_id, f"{await translate_async("Friend request from", language)} {detail.mention}!\n\n {await translate_async("Do you want to add them as a friend?", language)}", reply_markup=InlineKeyboardMarkup([
                     [InlineKeyboardButton(await translate_async("Accept", language), callback_data=f"accept_friend_{user_id}"), InlineKeyboardButton(await translate_async("Decline", language), callback_data="decline_friend")]
                ]))                
                await message.reply_text(await translate_async("Friend request sent successfully!", language))
            except UserBlocked:
                await message.reply_text(await translate_async("User has blocked the bot!", language))
            except RPCError as rc:
                await message.reply_text(await translate_async("Unable to send friend request! Please try again later.", language))
        except ValueError:
            await message.reply_text(await translate_async("Invalid ID!", language))
        except Exception as e:
            await message.reply_text(f"{await translate_async("Unable to send friend request!\n\ne", language)} {e}")