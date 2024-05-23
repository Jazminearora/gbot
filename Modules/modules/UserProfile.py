from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode
import asyncio

from Modules import cbot
import re

# Helper functions
from Modules.modules.advertisement import advert_user
from helpers.forcesub import subscribed, user_registered
from helpers.helper import get_profile, find_language, get_interest, get_age_group, get_gender
from langdb.get_msg import get_interest_reply_markup, get_reply_markup, get_lang_change
from helpers.translator import translate_async
from database.registerdb import add_user_id, store_str_id, remove_str_id , remove_user_id


# Define a regex pattern to match the button text
profile_pattern = re.compile(r"^👤 (Profile|Профиль|Profil) 👤$")

@cbot.on_message(filters.regex(profile_pattern) & filters.private & subscribed & user_registered)
async def handle_profile_response(client, message: Message):
    user_id = message.from_user.id
    language = find_language(user_id)
    await advert_user(user_id, language)
    text, reply_markup = await get_profile(user_id, language, "general")
    await message.reply_text(text, reply_markup=reply_markup)

@cbot.on_callback_query(filters.regex(r'^user_profile|user_statistics'))
async def handle_profile_statistics_callback(client, callback_query):
    user_id = callback_query.from_user.id
    language = find_language(user_id)
    mode = callback_query.data
    wait_message = await callback_query.message.edit_text("💭")
    try:
        profile_text, markup = await get_profile(user_id, language, mode)
        print(markup)
        await asyncio.sleep(0.2)
        try:
            await wait_message.edit_text(profile_text, parse_mode=ParseMode.MARKDOWN, reply_markup=markup)
        except Exception as e:
            await wait_message.edit_text(f"An error occurred: {str(e)}")
    except Exception as e:
        await wait_message.edit_text(f"An error occurred: {str(e)}")

@cbot.on_callback_query(filters.regex("^close_profile$"))
async def close_profile(client, callback_query):
    try:
        # Delete the callback message
        await callback_query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

@cbot.on_callback_query(filters.regex("^back(_home)?$"))
async def back(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        language = find_language(user_id)
        await advert_user(user_id, language)
        profile_type = "general" if callback_query.data == "back_home" else "user_profile"
        profile_text, reply_markup = await get_profile(user_id, language, profile_type)
        try:
            await callback_query.message.edit_caption(profile_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        except Exception as e:
            await callback_query.message.edit_caption(f"An error occurred: {str(e)}")
    except Exception as e:
        await callback_query.message.edit_caption(f"An error occurred: {str(e)}")

@cbot.on_callback_query(filters.regex("^edit_profile$"))
async def edit_profile(client, callback_query):
    try:
        # Get the user ID and language
        user_id = callback_query.from_user.id
        language = find_language(user_id)

        # Create the reply markup with the new buttons
        new_reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=await translate_async("Change language 🌐", language), callback_data="change_language"
                    ),
                    InlineKeyboardButton(
                        text=await translate_async("Change Gender 👤", language), callback_data="change_gender"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=await translate_async("Change Age Group 🎂", language), callback_data="change_age_group"
                    ),
                    InlineKeyboardButton(
                        text=await translate_async("Change Interest ❤️", language), callback_data="edit_interest"
                    ),
                ],
                [
                    InlineKeyboardButton(text=await translate_async("Back 🔙", language), callback_data="back"),
                    InlineKeyboardButton(text=await translate_async("Close ❌", language), callback_data="close_profile"),
                ],
            ]
        )


        # Edit the message with the new buttons
        await callback_query.message.edit_reply_markup(reply_markup=new_reply_markup)
    except Exception as e:
        print("Error in edit_profile:", e)

    
@cbot.on_callback_query(filters.regex("^change_language"))
async def change_language(client, callback_query):
    try:
        # Get the user ID and old language
        user_id = callback_query.from_user.id
        old_lang = find_language(user_id)
        caption, reply_markup = await get_lang_change(old_lang)
        # Edit the message with the new language options
        await callback_query.message.edit_caption(caption, reply_markup=reply_markup)
    except Exception as e:
        print("Error in change_language:", e)


# Callback function for setting the language
@cbot.on_callback_query(filters.regex("^set_language"))
async def set_language(client, callback_query):
    try:
        await callback_query.message.delete()
        user_id = callback_query.from_user.id
        # Extract the new language from the callback data
        new_lang = callback_query.data.split("_")[2]
        old_lang = find_language(user_id)
        remove_user_id(old_lang, user_id, old_lang)
        add_user_id(new_lang, user_id, new_lang)
        try:
            # If language change is successful, inform the user
            await callback_query.answer(f"↪️ {new_lang} ✅", show_alert=True)
            # Edit the message to display the success message in the new language
            if new_lang == "English":
                success_message = "Language changed successfully! 🇺🇸"
            elif new_lang == "Russian":
                success_message = "Язык успешно изменен! 🇷🇺"
            elif new_lang == "Azerbejani":
                success_message = "Dil uğurla dəyişdirildi! 🇦🇿"
            reply_markup = await get_reply_markup(new_lang)
            await cbot.send_message(user_id, success_message, reply_markup=reply_markup)
            
        except Exception as e:
            print("Error in changing language:", e)

    except Exception as e:
        print("Error in set_language:", e)


@cbot.on_callback_query(filters.regex("^change_gender$"))
async def change_gender(client, callback_query):
    print("function called")
    try:
        # Get the user ID and old language
        user_id = callback_query.from_user.id
        lang = find_language(user_id)
        markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Male👦", callback_data=f"set_gender_male")],
                [InlineKeyboardButton("Female👧", callback_data=f"set_gender_female")]
                ])
        txt = await translate_async("Choose your gender:", lang)
    except Exception as e:
        print("Error in change_gender:", e)

@cbot.on_callback_query(filters.regex("^set_gender.*$"))
async def set_interest(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        language = find_language(user_id)
        new_gender = callback_query.data.split("_")[2]
        muks = await callback_query.message.edit_caption("🔍")
        current_gender = get_gender(user_id, language).lower()
        try:
            remove_str_id(user_id, current_gender)  
        except Exception as e:
            print("Exception:", e)    
            return  
        trumk = await muks.edit_caption("🤖")
        try:
            store_str_id(user_id, new_gender)
        except Exception as e:
            print("Exception:", e) 
            return
        try:
            # If language change is successful, inform the user
            await callback_query.answer(f"↪️ {new_gender} ✅", show_alert=True)
            # Edit the message to display the success message in the new language
            success_message = await translate_async("Gender changed successfully!", language)
            reply_markup = await get_reply_markup(language)
            await trumk.edit_caption(success_message, reply_markup=reply_markup)
        except Exception as e:
            print("Error in changing language:", e)
    except Exception as e:
        print("Error in set_language:", e)

@cbot.on_callback_query(filters.regex("^edit_interest$"))
async def edit_interest(client, callback_query):
    try:
        # Get the user ID and language
        user_id = callback_query.from_user.id
        language = find_language(user_id)

        # Fetch current interest
        current_interest = get_interest(user_id, language)

        # Get reply markup and caption
        reply_arkup, captoion = await get_interest_reply_markup(current_interest, language)

        # Edit the message with the new interest options
        await callback_query.message.edit_caption(captoion, reply_markup=reply_arkup)

    except Exception as e:
        print("Error in edit_interest:", e)

@cbot.on_callback_query(filters.regex("^set_interest"))
async def set_interest(client, callback_query):
    try:
        user_id = callback_query.from_user.id
        language = find_language(user_id)
        new_interest = callback_query.data.split("_")[2]
        muks = await callback_query.message.edit_caption("🔍")
        current_interest = get_interest(user_id, language).lower()
        try:
            remove_str_id(user_id, current_interest)  
        except Exception as e:
            print("Exception:", e)    
            return  
        trumk = await muks.edit_caption("🤖")
        try:
            store_str_id(user_id, new_interest)
        except Exception as e:
            print("Exception:", e) 
            return
        try:
            # If language change is successful, inform the user
            await callback_query.answer(f"↪️ {new_interest} ✅", show_alert=True)
            # Edit the message to display the success message in the new language
            success_message = await translate_async("Interest changed successfully!", language)
            reply_markup = await get_reply_markup(language)
            await trumk.edit_caption(success_message, reply_markup=reply_markup)
        except Exception as e:
            print("Error in changing language:", e)
    except Exception as e:
        print("Error in set_language:", e)
