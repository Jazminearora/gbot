import re
from Modules import cbot
from pyrogram import filters
from Modules import cbot
from helpers.forcesub import subscribed, user_registered
from database.premiumdb import save_premium_user, is_user_premium, vip_users_details
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

button_pattern = re.compile(r"^(🔧 (Configure search|Настроить поиск|Axtarışı tənzimlə) 🔧)$")

@cbot.on_message(((filters.private & filters.regex(button_pattern)) | (filters.command("configure"))) & subscribed & user_registered)
async def configure_search(client, message):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Gender", callback_data="cgender"),
         InlineKeyboardButton("Age", callback_data="age"),
         InlineKeyboardButton("Room", callback_data="room")]
    ])
    await message.reply("Please select an option:", reply_markup=markup)

@cbot.on_callback_query(filters.regex("cgender"))
async def gender_callback(client, callback_query):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Male", callback_data="cmale"),
         InlineKeyboardButton("Female", callback_data="cfemale")],
        [InlineKeyboardButton("Any gender", callback_data="cany_gender"),
         InlineKeyboardButton("Back", callback_data="cback")]
    ])
    await callback_query.message.reply("Please select your gender:", reply_markup=markup)

@cbot.on_callback_query(filters.regex("cmale"))
async def male_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        await save_premium_user(user_id, gender="male")
        await callback_query.message.reply("Your gender has been updated to male.")
    else:
        await callback_query.message.reply("You need to be a premium user to update your gender.")

@cbot.on_callback_query(filters.regex("cfemale"))
async def female_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        await save_premium_user(user_id, gender="female")
        await callback_query.message.reply("Your gender has been updated to female.")
    else:
        await callback_query.message.reply("You need to be a premium user to update your gender.")

@cbot.on_callback_query(filters.regex("cany_gender"))
async def any_gender_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = await is_user_premium(user_id)
    if is_premium:
        await save_premium_user(user_id, gender="any gender")
        await callback_query.message.reply("Your gender has been updated to any gender.")
    else:
        await callback_query.message.reply("You need to be a premium user to update your gender.")

@cbot.on_callback_query(filters.regex("cback"))
async def cback_callback(client, callback_query):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Gender", callback_data="cgender"),
         InlineKeyboardButton("Age", callback_data="age"),
         InlineKeyboardButton("Room", callback_data="room")]
    ])
    await callback_query.message.reply("Please select an option:", reply_markup=markup)

@cbot.on_callback_query(filters.regex("age"))
async def age_callback(client, callback_query):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Below 18", callback_data="cbelow_18"),
         InlineKeyboardButton("18-24", callback_data="c18_24"),
         InlineKeyboardButton("25-34", callback_data="c25_34"),
         InlineKeyboardButton("Above 35", callback_data="cabove_35"),
         InlineKeyboardButton("Back", callback_data="gback")]
    ])
    await callback_query.message.reply("Please select your age group(s):", reply_markup=markup)

age_groups = {}

@cbot.on_callback_query(filters.regex(r"cbelow_18|c18_24|c25_34|cabove_35"))
async def age_group_callback(client, callback_query):
    user_id = callback_query.from_user.id
    age_group = callback_query.data
    if user_id not in age_groups:
        age_groups[user_id] = []
    age_groups[user_id].append(age_group)
    await callback_query.answer("Age group added!")

@cbot.on_callback_query(filters.regex("gback"))
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

