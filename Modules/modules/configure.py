import re
from Modules import cbot
from pyrogram import filters
from Modules import cbot
from helpers.forcesub import subscribed, user_registered
from database.premiumdb import save_premium_user, is_user_premium, vip_users_details
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

button_pattern = re.compile(r"^(🔧 (Configure search|Customize search|Modify search|Setup search) 🔧)$")

@cbot.on_message(((filters.private & filters.regex(button_pattern)) | (filters.command("configure"))) & subscribed & user_registered)
async def configure_search(client, message):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Gender", callback_data="cgndr"),
         InlineKeyboardButton("Age", callback_data="cage"),
         InlineKeyboardButton("Room", callback_data="crm")]
    ])
    await message.reply("Please select an option:", reply_markup=markup)

@cbot.on_callback_query(filters.regex("cgndr"))
async def gender_callback(client, callback_query):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Male", callback_data="cmle"),
         InlineKeyboardButton("Female", callback_data="cfem"),
         InlineKeyboardButton("Other", callback_data="cother")],
        [InlineKeyboardButton("Any gender", callback_data="cany_gndr"),
         InlineKeyboardButton("Go back", callback_data="cgoback")]
    ])
    await callback_query.message.reply("Please select your gender:", reply_markup=markup)

@cbot.on_callback_query(filters.regex("cmle"))
async def male_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        await save_premium_user(user_id, gender="male")
        await callback_query.message.reply("Your gender has been updated to male.")
    else:
        await callback_query.message.reply("You need to be a premium user to update your gender.")

@cbot.on_callback_query(filters.regex("cfem"))
async def female_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        await save_premium_user(user_id, gender="female")
        await callback_query.message.reply("Your gender has been updated to female.")
    else:
        await callback_query.message.reply("You need to be a premium user to update your gender.")

@cbot.on_callback_query(filters.regex("cother"))
async def other_gender_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        await save_premium_user(user_id, gender="other")
        await callback_query.message.reply("Your gender has been updated to other.")
    else:
        await callback_query.message.reply("You need to be a premium user to update your gender.")

@cbot.on_callback_query(filters.regex("cany_gndr"))
async def any_gender_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        await save_premium_user(user_id, gender="any gender")
        await callback_query.message.reply("Your gender has been updated to any gender.")
    else:
        await callback_query.message.reply("You need to be a premium user to update your gender.")

@cbot.on_callback_query(filters.regex("cgoback"))
async def cback_callback(client, callback_query):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Gender", callback_data="cgndr"),
         InlineKeyboardButton("Age", callback_data="cage"),
         InlineKeyboardButton("Room", callback_data="crm")]
    ])
    await callback_query.message.reply("Please select an option:", reply_markup=markup)

@cbot.on_callback_query(filters.regex("cage"))
async def age_callback(client, callback_query):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Below 18", callback_data="cblw_18"),
         InlineKeyboardButton("18-24", callback_data="c18_24"),
         InlineKeyboardButton("25-34", callback_data="c25_34"),
         InlineKeyboardButton("Above 35", callback_data="cabv_35"),
         InlineKeyboardButton("Go back", callback_data="agoback")]
    ])
    await callback_query.message.reply("Please select your age group(s):", reply_markup=markup)

age_groups = {}

@cbot.on_callback_query(filters.regex(r"cblw_18|c18_24|c25_34|cabv_35"))
async def age_group_callback(client, callback_query):
    user_id = callback_query.from_user.id
    age_group = callback_query.data
    if user_id not in age_groups:
        age_groups[user_id] = []
    age_groups[user_id].append(age_group)
    await callback_query.answer("Age group added!")

@cbot.on_callback_query(filters.regex("agoback"))
async def back_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in age_groups:
        age_groups_list = age_groups.pop(user_id)
        is_premium, _ = await is_user_premium(user_id)
        if is_premium:
            await save_premium_user(user_id, age_groups=age_groups_list)
            await callback_query.message.reply("Your age groups have been updated.")
        else:
            await callback_query.message.reply("You need to be a premium user to update your age groups.")
