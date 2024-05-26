import re
from Modules import cbot
from pyrogram import filters
from Modules import cbot
from helpers.forcesub import subscribed, user_registered
from database.premiumdb import save_premium_user, is_user_premium, vip_users_details
from helpers.helper import find_language
from helpers.translator import translate_async
from langdb.get_msg import get_interest_reply_markup
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

button_pattern = re.compile(r"^(🔧 (Configure search|Настроить поиск|Axtarışı tənzimlə) 🔧)$")

async def get_age_groups_text(user_id, lang):
    age_groups_list = vip_users_details(user_id, "age_groups")
    if age_groups_list:
        return "\n".join([f"• {age_group}" for age_group in age_groups_list])
    else:
        return await translate_async("Any.", lang)

@cbot.on_message(((filters.regex(button_pattern)) | (filters.command("configure"))) & filters.private  & subscribed & user_registered)
async def configure_search(client, message):
    lang = find_language(message.from_user.id)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(await translate_async("Gender🚻", lang), callback_data="cgndr"),
         InlineKeyboardButton(await translate_async("Age🕰️", lang), callback_data="cage"),
         InlineKeyboardButton(await translate_async("Room💡", lang), callback_data="crm")]
    ])
    await message.reply(await translate_async(f"""🔍 Search Configuration 🔍
                                              
--Current Configuration--:
Gender: {vip_users_details(message.from_user.id, "gender")}
Age Group(s): \n{await get_age_groups_text(message.from_user.id, lang)}  
Room: {vip_users_details(message.from_user.id, "room")}                                                                     

Please select an option for your search configuration:""", lang), reply_markup=markup)

@cbot.on_callback_query(filters.regex("cgndr"))
async def gender_callback(client, callback_query):
    lang = find_language(callback_query.from_user.id)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(await translate_async("👨Male", lang), callback_data="cmle"),
         InlineKeyboardButton(await translate_async("👩Female", lang), callback_data="cfem")],
        [InlineKeyboardButton(await translate_async("👤Any gender", lang), callback_data="cany_gndr"),
         InlineKeyboardButton(await translate_async("⬅️Go back", lang), callback_data="cgoback")]
    ])
    await callback_query.message.edit_caption(await translate_async("""🌐 Gender Selection 🌐
                                                                    
Please select your gender:""", lang), reply_markup=markup)

@cbot.on_callback_query(filters.regex("cmle"))
async def male_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = is_user_premium(user_id)
    lang = find_language(user_id)
    if is_premium:
        save_premium_user(user_id, gender="male")
        await callback_query.answer(await translate_async("Your gender has been updated to male.", lang), show_alert=True)
    else:
        await callback_query.answer(await translate_async("You need to be a premium user to update your gender.", lang), show_alert=True)

@cbot.on_callback_query(filters.regex("cfem"))
async def female_callback(client, callback_query):
    user_id = callback_query.from_user.id
    lang = find_language(user_id)
    is_premium, _ = is_user_premium(user_id)
    if is_premium:
        save_premium_user(user_id, gender="female")
        await callback_query.answer(await translate_async("Your gender has been updated to female.", lang), show_alert=True)
    else:
        await callback_query.answer(await translate_async("You need to be a premium user to update your gender.", lang), show_alert=True)

@cbot.on_callback_query(filters.regex("cany_gndr"))
async def any_gender_callback(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium, _ = is_user_premium(user_id)
    lang = find_language(user_id)
    if is_premium:
        save_premium_user(user_id, gender="any gender")
        await callback_query.answer(await translate_async("Your gender has been updated to any gender.", lang), show_alert=True)
    else:
        await callback_query.answer(await translate_async("You need to be a premium user to update your gender.", lang), show_alert=True)

@cbot.on_callback_query(filters.regex("cgoback"))
async def cback_callback(client, callback_query):
    lang = find_language(callback_query.from_user.id)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(await translate_async("Gender🚻", lang), callback_data="cgndr"),
         InlineKeyboardButton(await translate_async("Age🕰️", lang), callback_data="cage"),
         InlineKeyboardButton(await translate_async("Room💡", lang), callback_data="crm")]
    ])
    await callback_query.message.edit_caption(await translate_async(f"""🔍 Search Configuration 🔍
                                                                    
--Current Configuration--:
Gender: \n{vip_users_details(callback_query.from_user.id, "gender")}
Age Group(s): {await get_age_groups_text(callback_query.from_user.id, lang)}  
Room: {vip_users_details(callback_query.from_user.id, "room")}                                                                     

Please select an option for your search configuration:""", lang), reply_markup=markup)


@cbot.on_callback_query(filters.regex("cage"))
async def age_callback(client, callback_query):
    lang = find_language(callback_query.from_user.id)
    age_text = await get_age_groups_text(callback_query.from_user.id, lang)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"👶 {await translate_async('Below-18', lang)}", callback_data="cblw_18"),
         InlineKeyboardButton(f"🧑 {await translate_async('18-24', lang)}", callback_data="c18_24")],
        [ InlineKeyboardButton(f"🧑🏼 {await translate_async('25-34', lang)}", callback_data="c25_34"),
         InlineKeyboardButton(f"🧑🏽 {await translate_async('Above-35', lang)}", callback_data="cabv_35")],
        [ InlineKeyboardButton(f"⚙️ {await translate_async('Configure & back', lang)}", callback_data="agoback")]
    ])
    await callback_query.message.edit_caption(await translate_async("Please select your age group(s) and click back to configure:\n\n" + f"Current configuration:\n{age_text}" + f"\n\nNote: The configuration will update after you select and click Configure & back button!", lang), reply_markup=markup)


age_groups = {}

@cbot.on_callback_query(filters.regex(r"cblw_18|c18_24|c25_34|cabv_35"))
async def age_group_callback(client, callback_query):
    user_id = callback_query.from_user.id
    lang = find_language(user_id)
    age_group = callback_query.data
    if user_id not in age_groups:
        age_groups[user_id] = []
    # Convert callback data to proper age group format
    age_group_text = {
        "cblw_18": "Below-18",
        "c18_24": "18-24",
        "c25_34": "25-34",
        "cabv_35": "Above-35"
    }.get(age_group)
    age_groups[user_id].append(age_group_text)
    await callback_query.answer(await translate_async("Age group added!", lang), show_alert=True)

@cbot.on_callback_query(filters.regex("agoback"))
async def back_callback(client, callback_query):
    user_id = callback_query.from_user.id
    lang = find_language(user_id)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(await translate_async("Gender🚻", lang), callback_data="cgndr"),
         InlineKeyboardButton(await translate_async("Age🕰️", lang), callback_data="cage"),
         InlineKeyboardButton(await translate_async("Room💡", lang), callback_data="crm")]
    ])
    if user_id in age_groups:
        age_groups_list = age_groups.pop(user_id)
        is_premium, _ = is_user_premium(user_id)
        if is_premium:
            save_premium_user(user_id, age_groups=age_groups_list)
            await callback_query.answer(await translate_async("Your age groups have been updated.", lang), show_alert=True)
        else:
            await callback_query.answer(await translate_async("You need to be a premium user to update your age groups.", lang), show_alert=True)

    await callback_query.message.edit_caption(await translate_async(f"""🔍 Search Configuration 🔍

--Current Configuration--:
Gender: {vip_users_details(callback_query.from_user.id, "gender")}
Age Group(s): \n{await get_age_groups_text(callback_query.from_user.id, lang)}  
Room: {vip_users_details(callback_query.from_user.id, "room")}                                                                     

Please select an option for your search configuration:""", lang), reply_markup=markup)

@cbot.on_callback_query(filters.regex("crm"))
async def room_callback(client, callback_query):
    user_id = callback_query.from_user.id
    lang = find_language(user_id)
    cr_room = vip_users_details(user_id, "room")

    reply_markup, _ = await get_interest_reply_markup("_", language="English")
    new_inline_keyboard = []
    for row in reply_markup.inline_keyboard[:-1]:
        new_row = []
        for button in row:
            if button.callback_data.startswith("set_interest"):
                button.callback_data = button.callback_data.replace("set_interest", "config")
            new_row.append(button)
        new_inline_keyboard.append(new_row)
    new_inline_keyboard.append([
        InlineKeyboardButton(await translate_async("❌ Any", lang), callback_data="config_any"),
        InlineKeyboardButton(await translate_async("Back 🔙", lang), callback_data="cgoback")
    ])
    new_reply_markup = InlineKeyboardMarkup(new_inline_keyboard)
    await callback_query.message.edit_caption(await translate_async(f"Current Configuration: {cr_room}\n\nPlease select the room for your search configuration:", lang), reply_markup=new_reply_markup)


@cbot.on_callback_query(filters.regex(r"^config_"))
async def room_configuration_callback(client, callback_query):
    user_id = callback_query.from_user.id
    lang = find_language(user_id)
    room_type = callback_query.data.replace("config_", "")
    is_premium, _ = is_user_premium(user_id)
    if is_premium:
        save_premium_user(user_id, room=room_type)
        await callback_query.answer(await translate_async(f"Your room configuration has been updated to {room_type}.", lang), show_alert=True)
    else:
        await callback_query.answer(await translate_async("You need to be a premium user to update your interest.", lang), show_alert=True)



    # reply_markup = InlineKeyboardMarkup([
    # [InlineKeyboardButton(await translate_async("👥 Communication", lang), callback_data="config_communication")],
    # [InlineKeyboardButton(await translate_async("💕 Intimacy", lang), callback_data="config_intimacy")],
    # [InlineKeyboardButton(await translate_async("💰 Selling", lang), callback_data="config_selling")],
    # [InlineKeyboardButton(await translate_async("🎬 Movies", lang), callback_data="config_movies")],
    # [InlineKeyboardButton(await translate_async("🎌 Anime", lang), callback_data="config_anime")],
    # [InlineKeyboardButton(await translate_async("❌ Any", lang), callback_data="config_any"),
    #  InlineKeyboardButton(await translate_async("Back 🔙", lang), callback_data="cgoback")]
    # ])