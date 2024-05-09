from pyrogram import filters
import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from Modules import cbot, BOT_USERNAME
from helpers.helper import find_language, get_gender, get_age_group, get_interest, is_user_registered
from langdb.get_msg import get_registration_text, get_reply_markup
from helpers.translator import translate_text
from database.registerdb import add_user_id
from database.referdb import save_id, is_served_user, get_point
from database.premiumdb import extend_premium_user_hrs, save_premium_user
from helpers.forcesub import subscribed, user_registered
from config import EXTEND_HRS_REFER




async def get_user_name(user_id):
    try:
        user = await cbot.get_users(user_id)
        if user:
            name = user.first_name
            if user.last_name:
                name += " " + user.last_name
            return name
    except Exception as e:
        return None
    
async def check_registration_completed(user_id):
    # Check if the user has completed registration within a specified time period.
    max_attempts = 12  # 12 attempts at 5-second intervals = 60 seconds
    for attempt in range(max_attempts):
        if is_user_registered(user_id):
            return True  # User is registered
        await asyncio.sleep(5)  # Wait for 5 seconds before next attempt

@cbot.on_message(filters.command(["start"]) & filters.private & subscribed & ~user_registered)
async def register_user(client, message):
    # Extract the referer user id from the command message
    command_parts = message.text.split(" ")
    if len(command_parts) > 1:
        try:
            referer_user_id = int(command_parts[1].replace("r", ""))
        except ValueError:
            await message.reply("Invalid referer user id format.")
            return
        name = await get_user_name(referer_user_id)
        if name is not None:
            try:
                user_id = message.from_user.id
                if command_parts:
                    # Check if the sender user ID has already been referred
                    is_referred = await is_served_user(user_id)
                    if not is_referred:
                        # Check if the user is already registered
                        is_registered =  is_user_registered(user_id)
                        if not is_registered:
                            await message.reply("Please Register now to complete Referal.")
                            try:
                                # Save the sender user ID as referred by the referer user ID
                                language = find_language(user_id)
                                # Check if user ID is already registered
                                if language:
                                    gender = get_gender(user_id, language)
                                    if gender:
                                        age = get_age_group(user_id, language)
                                        if age:
                                            interest = get_interest(user_id, language)
                                            if interest:
                                                msg = "You are Already registered!"
                                                if language == "English":
                                                    await message.reply_text(msg)
                                                elif user_lang == "Russian":
                                                    await message.reply_text(translate_text(msg, target_language="ru"))
                                                elif user_lang == "Azerbejani":
                                                    await message.reply_text(translate_text(msg, target_language="az"))
                                            else:
                                                caption, reply_markup = await get_registration_text(language, "interest")
                                                await message.reply_text(caption, reply_markup=reply_markup)
                                        else:
                                            caption, reply_markup = await get_registration_text(language, "age")
                                            await message.reply_text(caption, reply_markup=reply_markup)
                                    else:
                                        caption, reply_markup = await get_registration_text(language, "gender")
                                        await message.reply_text(caption, reply_markup=reply_markup)
                                else:
                                    caption= f"Choose your language\nВыберите ваш язык\ndilinizi seçin:"
                                    reply_markup = InlineKeyboardMarkup([
                                        [InlineKeyboardButton("English", callback_data="register_language_English")],
                                        [InlineKeyboardButton("Русский", callback_data="register_language_Russian")],
                                        [InlineKeyboardButton("Azərbaycan", callback_data="register_language_Azerbejani")]])
                                    await message.reply_text(caption, reply_markup=reply_markup)
                            except Exception as e:
                              print("Error in register_user:", e)
                            if not await check_registration_completed(user_id):
                                button = InlineKeyboardMarkup([
                                        [
                                            InlineKeyboardButton(
                                                text='Try Again',
                                                url=f"https://t.me/{BOT_USERNAME}?start={message.command[1]}"
                                            )
                                        ]
                                    ])
                                await message.reply_text(f"You are not registered yet!\n\nUse below button to retry.", reply_markup = button)
                                return
                            await save_id(referer_user_id, user_id)
                            referer_lang = find_language(referer_user_id)
                            if referer_lang == "English":
                                message_text = f"You are successfully referred by {name}."
                            elif referer_lang == "Russian":
                                message_text = f"Вас успешно направил {name}.."
                            elif referer_lang == "Azerbejani":
                                message_text = f"Siz {name} tərəfindən uğurla istinad edildiniz."
                            else:
                                # Default to English if the language is not recognized
                                message_text = f"You are successfully referred by {name}."
                            await message.reply_text(message_text)
                            extend_premium_user_hrs(referer_user_id, EXTEND_HRS_REFER)
                            referer_lang = find_language(referer_user_id)
                            referred_name = await get_user_name(user_id)
                            total_points =await (get_point(referer_user_id))
                            caption_prefix = "You have successfully referred to"
                            caption_suffix = f".\n\n Your Total points: {total_points}"
                            if referer_lang == "English":
                                await cbot.send_message(referer_user_id, f"{caption_prefix} {referred_name}{caption_suffix}")
                            elif referer_lang == "Russian":
                                translated_caption = translate_text(caption_prefix, target_language="ru") + f" {referred_name}" + translate_text(caption_suffix, target_language="ru")
                                await cbot.send_message(referer_user_id, translated_caption)
                            elif referer_lang == "Azerbejani":
                                translated_caption = translate_text(caption_prefix, target_language="az") + f" {referred_name}" + translate_text(caption_suffix, target_language="az")
                                await cbot.send_message(referer_user_id, translated_caption)
                        else:
                            msg = "You are Already registered!"
                            user_lang = find_language(user_id)
                            translations = {"English": msg, "Russian": translate_text(msg, target_language="ru"), "Azerbejani": translate_text(msg, target_language="az")}
                            await message.reply_text(translations.get(user_lang, msg))
                    else:
                        await message.reply_text("You are already refered by someone!")
            except Exception as e:
                await message.reply_text(f"An error occurred: {str(e)}")
        else:
            await message.reply_text(f"Referer id {referer_user_id} is invalid.")
    else:
        try:
            if is_user_registered(message.from_user.id):
                await message.reply_text("You are already registered.")
                return
            # Get user ID
            user_id = message.from_user.id
            language = find_language(user_id)
            # Check if user ID is already registered
            if language:
                gender = get_gender(user_id, language)
                if gender:
                    age = get_age_group(user_id, language)
                    if age:
                        interest = get_interest(user_id, language)
                        if interest:
                            await message.reply_text("You are already registered.")
                        else:
                            caption, reply_markup = await get_registration_text(language, "interest")
                            await message.reply_text(caption, reply_markup=reply_markup)
                    else:
                        caption, reply_markup = await get_registration_text(language, "age")
                        await message.reply_text(caption, reply_markup=reply_markup)
                else:
                    caption, reply_markup = await get_registration_text(language, "gender")
                    await message.reply_text(caption, reply_markup=reply_markup)
            else:
                caption= f"Choose your language\nВыберите ваш язык\ndilinizi seçin:"
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("English", callback_data="register_language_English")],
                    [InlineKeyboardButton("Русский", callback_data="register_language_Russian")],
                    [InlineKeyboardButton("Azərbaycan", callback_data="register_language_Azerbejani")]])
                await message.reply_text(caption, reply_markup=reply_markup)
        except Exception as e:
            print("Error in register_user:", e)

@cbot.on_callback_query(filters.regex(r"^register_language_"))
async def register_language_callback(client, callback_query):
    try:
        # Extract language from callback data
        language = callback_query.data.split("_")[2]
        
        # Get user ID
        user_id = callback_query.from_user.id
        lang_chk = find_language(user_id)
        if not lang_chk:
            # Store user ID in chosen language's 'users' field in MongoDB
            add_user_id(language, user_id, language)  
            caption, reply_markup = await get_registration_text(language, "gender")
            await callback_query.message.edit_text(caption, reply_markup=reply_markup)    
        else:
            await callback_query.message.edit_text("You have already selected a language.")
    except Exception as e:
        print("Error in register_language_callback:", e)

@cbot.on_callback_query(filters.regex(r"^register_gender_"))
async def register_gender_callback(client, callback_query):
    try:
        # Extract language and gender from callback data
        data_parts = callback_query.data.split("_")
        language = data_parts[2]
        gender = data_parts[3]
        
        # Get user ID
        user_id = str(callback_query.from_user.id)
        
        # Check if user ID is already registered for gender
        if not get_gender(user_id, language):
            # Store user ID in chosen gender's field in the chosen language in MongoDB
            add_user_id(language, user_id, gender)
            
            # Ask user to choose age group
            caption, reply_markup = await get_registration_text(language, "age")
            await callback_query.message.edit_text(caption, reply_markup=reply_markup)
        else:
            await callback_query.message.edit_text("You have already selected a gender.")
    except Exception as e:
        print("Error in register_gender_callback:", e)

# Callback to handle age group selection
@cbot.on_callback_query(filters.regex(r"^register_age_"))
async def register_age_callback(client, callback_query):
    try:
        # Extract language and age group from callback data
        data_parts = callback_query.data.split("_")
        language = data_parts[2]
        age_group = data_parts[3].replace("-", "_")
        
        # Get user ID
        user_id = str(callback_query.from_user.id)
        
        # Check if user ID is already registered for age group
        if not get_age_group(user_id, language):
            # Store user ID in chosen age group's field in the chosen language in MongoDB
            add_user_id(language, user_id, age_group)
            
            # Ask user to choose interest
            caption, reply_markup = await get_registration_text(language, "interest")
            await callback_query.message.edit_text(caption, reply_markup=reply_markup)
        else:
            await callback_query.message.edit_text("You have already selected an age group.")
    except Exception as e:
        print("Error in register_age_callback:", e)

# Callback to handle interest selection
@cbot.on_callback_query(filters.regex(r"^register_interest_"))
async def register_interest_callback(client, callback_query):
    try:
        # Extract language and interest from callback data
        data_parts = callback_query.data.split("_")
        language = data_parts[2]
        interest = data_parts[3]
        
        # Get user ID
        user_id = str(callback_query.from_user.id)
        
        # Check if user ID is already registered for interest
        if not get_interest(user_id,language):
            # Store user ID in chosen interest's field in the chosen language in MongoDB
            add_user_id(language, user_id, interest)
            
            # Registration completed
            await callback_query.message.edit_text("Registration completed! Thank you for registering.")
            save_premium_user(user_id, premium_status= False)
            reply_markup = await get_reply_markup(language)
            await callback_query.message.reply_text("Please select a option.", reply_markup=reply_markup)
        else:
            await callback_query.message.edit_text("You have already selected an interest.")
    except Exception as e:
        print("Error in register_interest_callback:", e)
