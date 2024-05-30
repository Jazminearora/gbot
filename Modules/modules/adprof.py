import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, PeerIdInvalid, MessageNotModified


from helpers.helper import find_language, get_profile
from Modules.modules.register import get_user_name
from database.residuedb import add_bluser, is_blocked as is_blckd, unblock_user
from database.premiumdb import vip_users_details, save_premium_user
from .. import cbot, ADMIN_IDS, BOT_NAME


async def get_genral_markup(user_id):
    genral_markup =  InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Info", callback_data=f'info_{user_id}'),
            InlineKeyboardButton("📣 Notify", callback_data=f'notify_{user_id}')],
            [InlineKeyboardButton("🛑 Block Media", callback_data=f'block_media_{user_id}'),
            InlineKeyboardButton("🚷 Block User", callback_data=f'block_completely_{user_id}')],
            [InlineKeyboardButton("✅ Verify", callback_data=f'verify_{user_id}')],
            [InlineKeyboardButton("❌ Close", callback_data='st_close')]
        ])
    return genral_markup


@cbot.on_message(filters.command("id", prefixes= ["/", ".", "#"]) & filters.user(ADMIN_IDS) & filters.private)
async def user_ditales(_, message):
    try:
        command = message.text
        user_id = int(command.split()[1])
    except (ValueError, IndexError):
        await message.reply("Usage: #id <user_id>\nSupported prefixes: '/' '.' '#'")
        return
    await message.reply("Please choose a option from below", reply_markup= await get_genral_markup(user_id))


@cbot.on_callback_query(filters.regex("info_(.+)"))
async def get_user_info(_, query: CallbackQuery):
    try:
        user_id = int(query.data.split("_")[1])
        raw_text1, _ = await get_profile(user_id, "English", "user_profile")
        raw_text2, _ = await get_profile(user_id, "English", "user_statistics")
        raw_text = f"{raw_text1}\n\n{raw_text2}"
        lang = find_language(user_id)
        profile_text = raw_text.replace("English", lang)
        blckd = await is_blckd(user_id)
        profile_text += f"\n🚷Blocked Status: {blckd}"
        profile_text += f"\n🚫🎥Blocked Media: {vip_users_details(user_id, "block_media") if vip_users_details(user_id, "block_media") else "False"}"
        profile_text += f"\n☑️Verify Status: {vip_users_details(user_id, "verified") if vip_users_details(user_id, "verified") else "False"}"
        # profile_text += f"\n\n🔍Searching status: {searching}"
        markup = await get_genral_markup(user_id)
        if query.message.text == profile_text:
            return
        await query.message.edit_text(profile_text, reply_markup= markup)
    except Exception as e:
        await query.message.reply(f"An error occured: {e}")


@cbot.on_callback_query(filters.regex("block_completely_(.+)"))
async def block_user_completely(_, query):
    try:
        user_id = int(query.data.split("_")[2])
        markup = await get_genral_markup(user_id)
        if not await is_blckd(user_id):
            await add_bluser(user_id)
            await query.message.edit_text("User Blocked Completely", reply_markup= markup)
        else:
            await unblock_user(int(user_id))
            await query.message.edit_text("User unblocked", reply_markup= markup)
    except MessageNotModified:
        pass
    except Exception as e:
        await query.message.reply(f"An error occured: {e}")

@cbot.on_callback_query(filters.regex("block_media_(.+)"))
async def block_user_media(_, query):
    try:
        user_id = int(query.data.split("_")[2])
        markup = await get_genral_markup(user_id)
        if not vip_users_details(user_id, "block_media"):
            save_premium_user(user_id, block_media= True)
            await query.message.edit_text("User Media Blocked.", reply_markup= markup)
        else:
            save_premium_user(user_id, block_media= False)
            await query.message.edit_text("User Media unblocked.", reply_markup= markup)
    except MessageNotModified:
        pass
    except Exception as e:
        await query.message.reply(f"An error occured: {e}")


@cbot.on_callback_query(filters.regex("verify_(.+)"))
async def verify_user(_, query):
    try:
        user_id = int(query.data.split("_")[1])
        markup = await get_genral_markup(user_id)
        if not vip_users_details(user_id, "verified"):
            save_premium_user(user_id, verified= True)
            await query.message.edit_text("User verified successfully.", reply_markup= markup)
        else:
            await query.message.edit_text("User is Already verified.", reply_markup= markup)
    except MessageNotModified:
        pass
    except Exception as e:
        await query.message.reply(f"An error occured: {e}")

# function to notify users:
@cbot.on_callback_query(filters.regex("notify_(.+)"))
async def notify_user(_, query: CallbackQuery):
    user_id = int(query.data.split("_")[1])
    markup = await get_genral_markup(user_id)        
    notify_msg = f"""
👋 Hello {await get_user_name(user_id)}!

We noticed you haven't engaged in a while. 🌟 It's the perfect time to discover new friends and enrich your experience! 🌐🎉

✨ Start a conversation today and see what amazing connections you can make! 💬🤝

Best,
{BOT_NAME} Team 🚀
"""
    try:
        await cbot.send_message(user_id, notify_msg)
        await query.answer("User notified successfully!!", show_alert= True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        cbot.send_message(user_id, notify_msg)
    except InputUserDeactivated:
        await query.message.reply(f"User {user_id} has deactivated their ID!")
    except UserIsBlocked:
        await query.message.reply(f"User {user_id} has blocked the bot!")
    except PeerIdInvalid:
        await query.message.reply(f"User {user_id} has an invalid ID!")
    except Exception as e:
        await query.message.reply(f"An error occurred with user {user_id}: {e}")