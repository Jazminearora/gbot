from pyrogram.errors import UserBlocked, UserIdInvalid, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, User
import pyrostep

from database.premiumdb import vip_users_details
from Modules import cbot
from helpers.translator import translate_async

pyrostep.listen(cbot)

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
            try:
                await message.reply_text(await translate_async("Enter a nickname for your friend:", language))
                ask = await pyrostep.wait_for(message.from_user.id, timeout = 45)
                nickname = ask.text
            except TimeoutError:
                await message.reply_text(await translate_async("No nickname received!!", language))
                return
            try:
                detail: User = await client.get_users(user_id)
                await cbot.send_message(friend_id, f"{await translate_async("Friend request from  your interlocutor.\n\n Do you want to add them as a friend?", language)}", reply_markup=InlineKeyboardMarkup([
                     [InlineKeyboardButton(await translate_async("Accept", language), callback_data=f"accept_friend_{user_id}_{nickname}"), InlineKeyboardButton(await translate_async("Decline", language), callback_data="decline_friend")]
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