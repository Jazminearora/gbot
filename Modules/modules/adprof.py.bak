from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from .new_search import is_user_searching
from helpers.helper import find_language, get_profile
from database.residuedb import add_bluser, is_blocked
from .. import cbot, ADMIN_IDS


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


@cbot.on_message(filters.command("profile") & filters.user(ADMIN_IDS))
async def get_users_profile(_, message: Message):
    print("adminprofile")
    try:
        command = message.text
        user_id = int(command.split()[1])
    except (ValueError, IndexError):
        await message.reply("Usage: /profile <user_id>")
        return
    markup = await get_genral_markup(user_id)
    await message.reply("Please choose a option from below", reply_markup= markup)

@cbot.on_callback_query(filters.regex("info_(.+)"))
async def get_user_info(_, query: CallbackQuery):
    try:
        user_id = int(query.data.split("_")[1])
        raw_text, _ = await get_profile(user_id, "English")
        lang = find_language(user_id)
        profile_text = raw_text.replace("English", lang)
        blckd = await is_blocked(user_id)
        profile_text += f"\n🚷Blocked Status: {blckd}"
        searching = await is_user_searching(user_id)
        profile_text += f"\n\n🔍Searching status: {searching}"
        markup = await get_genral_markup(user_id)
        await query.message.edit_text(profile_text, reply_markup= markup)
    except Exception as e:
        await query.message.reply(f"An error occured: {e}")


@cbot.on_callback_query(filters.regex("block_completely_(.+)"))
async def block_user_completely(_, query: CallbackQuery):
    try:
        user_id = int(query.data.split("_")[2])
        markup = await get_genral_markup(user_id)
        if not await is_blocked(user_id):
            await add_bluser(user_id)
            await query.message.edit_text("User Blocked Completely", reply_markup= markup)
        else:
            await query.message.edit_text("User is Already Blocked Completely.", reply_markup= markup)
    except Exception as e:
        await query.message.reply(f"An error occured: {e}")