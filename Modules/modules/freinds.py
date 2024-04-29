from pyrogram import filters, Client
from pyrogram.errors import UserBlocked, UserIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.premiumdb import save_premium_user, vip_users_details
from.. import cbot
import pyrostep
from helpers.helper import is_user_registered

pyrostep.listen(cbot)


@cbot.on_message(filters.command("frens"))
async def frens(client, message):
    user_id = message.from_user.id
    frens_list = await vip_users_details(user_id, "frens")
    keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Add friend", callback_data="add_friend")]
        ])
    if frens_list:
        frens_text = "Here is the list of your friends:\n"
        for friend_id in frens_list:
            detail = await client.get_users(friend_id)
            frens_text += f"@{detail.mention}\n"
        await message.reply_text(frens_text, reply_markup=keyboard)
    else:
        await message.reply_text("You don't have any friends yet!\n\n Add your friends now!", reply_markup=keyboard)

@cbot.on_callback_query(filters.regex("add_friend"))
async def add_friend(client, query):
    user_id = query.from_user.id
    await query.message.reply_text("Enter the ID of the friend you want to add:")
    friend_id_input = await pyrostep.wait_for(user_id)
    friend_id = friend_id_input.text
    try:
        await client.get_users(friend_id)
    except UserIdInvalid:
        await query.message.reply_text("User ID invalid")
    if friend_id!= str(query.from_user.id):
        try:
            friend_id = int(friend_id)
            try:
                await client.send_message(friend_id, f"Friend request from @{query.from_user.username}! Do you want to add them as a friend?", reply_markup=InlineKeyboardMarkup([
                     [InlineKeyboardButton("Accept", callback_data=f"accept_friend_{user_id}"), InlineKeyboardButton("Decline", callback_data="decline_friend")]
                    ]))                
                await query.message.reply_text("Friend request sent successfully!")
            except UserBlocked:
                await query.message.reply_text("User has blocked the bot!")
            except:
                await query.message.reply_text("Unable to send friend request!")
        except ValueError:
            await query.message.reply_text("Invalid ID!")
        except:
            await query.message.reply_text("Unable to send friend request!")

@cbot.on_callback_query(filters.regex("accept_friend_"))
async def accept_friend(client, query):
    user_id = int(query.data.split("_")[2])
    friend_id = query.from_user.id
    await query.message.reply_text("You have accepted the friend request!")
    await cbot.send_message(user_id, f"@{query.from_user.username} has accepted your friend request!")
    await save_premium_user(user_id, frens=[friend_id])
    await save_premium_user(friend_id, frens=[user_id])

@cbot.on_callback_query(filters.regex("decline_friend"))
async def decline_friend(client, query):
    await query.message.edit_text("You have declined the friend request!")