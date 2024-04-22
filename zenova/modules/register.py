from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from zenova import mongodb, zenova
from helpers.helper import find_language, add_user_id, get_gender, get_age_group, get_interest, is_user_registered
from helpers.get_msg import get_registration_text
    
@zenova.on_message(filters.command(["register"]) & filters.private)
async def register_user(client, message):
    try:
        if is_user_registered(message.from_user.id):
            await message.reply_text("You are already registered.")
            return
        # Get user ID
        user_id = message.from_user.id
        language = find_language(user_id)
        print("register.py language fetched:", language)
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
                        caption, reply_markup = get_registration_text(language, "interest")
                        await message.reply_text(caption, reply_markup=reply_markup)
                else:
                    caption, reply_markup = get_registration_text(language, "age")
                    await message.reply_text(caption, reply_markup=reply_markup)
            else:
                caption, reply_markup = get_registration_text(language, "gender")
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

@zenova.on_callback_query(filters.regex(r"^register_language_"))
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
            caption, reply_markup = get_registration_text(language, "gender")
            await callback_query.message.edit_text(caption, reply_markup=reply_markup)    
        else:
            await callback_query.message.edit_text("You have already selected a language.")
    except Exception as e:
        print("Error in register_language_callback:", e)

@zenova.on_callback_query(filters.regex(r"^register_gender_"))
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
            caption, reply_markup = get_registration_text(language, "age")
            await callback_query.message.edit_text(caption, reply_markup=reply_markup)
        else:
            await callback_query.message.edit_text("You have already selected a gender.")
    except Exception as e:
        print("Error in register_gender_callback:", e)

# Callback to handle age group selection
@zenova.on_callback_query(filters.regex(r"^register_age_"))
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
            caption, reply_markup = get_registration_text(language, "interest")
            await callback_query.message.edit_text(caption, reply_markup=reply_markup)
        else:
            await callback_query.message.edit_text("You have already selected an age group.")
    except Exception as e:
        print("Error in register_age_callback:", e)

# Callback to handle interest selection
@zenova.on_callback_query(filters.regex(r"^register_interest_"))
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
        else:
            await callback_query.message.edit_text("You have already selected an interest.")
    except Exception as e:
        print("Error in register_interest_callback:", e)
