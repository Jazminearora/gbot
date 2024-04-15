from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from zenova import mongodb, zenova
from helpers.helper import find_language, add_user_id, get_gender, get_age_group, get_interest, is_user_registered


# Register command to initiate user registration process
@zenova.on_message(filters.command(["register"]) & filters.private)
async def register_user(client, message):
    try:
        if is_user_registered(message.from_user.id):
            await message.reply_text("You are already registered.")
            return
        # Get user ID
        user_id = message.from_user.id
        print("user_id:", user_id)
        language = find_language(user_id)
        # Check if user ID is already registered
        if language:
            gens= get_gender(user_id)
            print("gens:", gens)
            if get_gender(message.from_user.id):
                age = get_age_group(user_id)
                if age:
                    interest = get_interest(user_id)
                    if interest:
                        await message.reply_text("You are already registered.")
                    else:
                        interest_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("👁‍🗨 Communication", callback_data=f"register_interest_{language}_communication")],
                        [InlineKeyboardButton("🔞 Intimacy (18+)", callback_data=f"register_interest_{language}_intimacy")],
                        [InlineKeyboardButton("🚼 Selling sex (18+)", callback_data=f"register_interest_{language}_selling")]])
                        await message.reply_text("Choose your intrest:", reply_markup=interest_markup)
                else:
                    age_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Below 18", callback_data=f"register_age_{language}_below_18")],
                [InlineKeyboardButton("18-24", callback_data=f"register_age_{language}_18_24")],
                [InlineKeyboardButton("25-34", callback_data=f"register_age_{language}_25_34")],
                [InlineKeyboardButton("Above 35", callback_data=f"register_age_{language}_above_35")]])
                    await message.reply_text("Choose your age group:", reply_markup=f"{age_markup}")
            else:
                gender_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Male👦", callback_data=f"register_gender_{language}_male")],
                    [InlineKeyboardButton("Female👧", callback_data=f"register_gender_{language}_female")]])
                await message.reply_text("Choose your gender:", reply_markup=gender_markup)
        else:
            # Ask user to choose language
            await message.reply_text("Choose your language:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("English", callback_data="register_language_English")],
                [InlineKeyboardButton("Russian", callback_data="register_language_Russian")],
                [InlineKeyboardButton("Azerbejani", callback_data="register_language_Azerbejani")]]))
    except Exception as e:
        print("Error in register_user:", e)

# Callback to handle language selection
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
            add_user_id(language, user_id, "users")  
            await callback_query.message.edit_text("Choose your gender:", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Male👦", callback_data=f"register_gender_{language}_male")],
                    [InlineKeyboardButton("Female👧", callback_data=f"register_gender_{language}_female")]]))    
        else:
            await callback_query.message.edit_text("You have already selected a language.")
    except Exception as e:
        print("Error in register_language_callback:", e)

# Callback to handle gender selection
@zenova.on_callback_query(filters.regex(r"^register_gender_"))
async def register_gender_callback(client, callback_query):
    try:
        # Extract language and gender from callback data
        data_parts = callback_query.data.split("_")
        language = data_parts[2]
        gender = data_parts[3]
        
        # Get user ID
        user_id = str(callback_query.from_user.id)
        print('query id:', user_id)
        
        # Check if user ID is already registered for gender
        if not get_gender(user_id):
            # Store user ID in chosen gender's field in the chosen language in MongoDB
            add_user_id(language, user_id, gender)
            
            # Ask user to choose age group
            await callback_query.message.edit_text("Choose your age group:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Below 18", callback_data=f"register_age_{language}_below-18")],
                [InlineKeyboardButton("18-24", callback_data=f"register_age_{language}_18-24")],
                [InlineKeyboardButton("25-34", callback_data=f"register_age_{language}_25-34")],
                [InlineKeyboardButton("Above 35", callback_data=f"register_age_{language}_above-35")]]))
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
        if not get_age_group(user_id):
            # Store user ID in chosen age group's field in the chosen language in MongoDB
            add_user_id(language, user_id, age_group)
            
            # Ask user to choose interest
            await callback_query.message.edit_text("Choose your interest:", reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("👁‍🗨 Communication", callback_data=f"register_interest_{language}_communication")],
                        [InlineKeyboardButton("🔞 Intimacy (18+)", callback_data=f"register_interest_{language}_intimacy")],
                        [InlineKeyboardButton("🚼 Selling sex (18+)", callback_data=f"register_interest_{language}_selling")]]))
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
        if not get_interest(user_id):
            # Store user ID in chosen interest's field in the chosen language in MongoDB
            add_user_id(language, user_id, interest)
            
            # Registration completed
            await callback_query.message.edit_text("Registration completed! Thank you for registering.")
        else:
            await callback_query.message.edit_text("You have already selected an interest.")
    except Exception as e:
        print("Error in register_interest_callback:", e)
