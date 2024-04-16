from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.helper import get_profile, find_language, edit_language

# callback handler
@Client.on_callback_query(filters.regex("^close_profile$"))
def close_profile(client, callback_query):
    try:
        # Delete the callback message
        callback_query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

@Client.on_callback_query(filters.regex("^edit_profile$"))
def edit_profile(client, callback_query):
    try:
        # Get the user ID and language
        user_id = callback_query.from_user.id
        language = find_language(user_id)

        # Create the reply markup with the new buttons
        if language == "English":
            change_language_button = InlineKeyboardButton("Change language 🌐", callback_data="change_language")
            gender_interest_buttons = [InlineKeyboardButton("Gender 👤", callback_data="edit_gender"), InlineKeyboardButton("Interest ❤️", callback_data="edit_interest")]
            age_group_button = InlineKeyboardButton("Age group 🎂", callback_data="edit_age_group")
            back_close_buttons = [InlineKeyboardButton("Back 🔙", callback_data="back"), InlineKeyboardButton("Close ❌", callback_data="close_profile")]
        elif language == "Russian":
            change_language_button = InlineKeyboardButton("Изменить язык 🌐", callback_data="change_language")
            gender_interest_buttons = [InlineKeyboardButton("Пол 👤", callback_data="edit_gender"), InlineKeyboardButton("Интерес ❤️", callback_data="edit_interest")]
            age_group_button = InlineKeyboardButton("Возрастная группа 🎂", callback_data="edit_age_group")
            back_close_buttons = [InlineKeyboardButton("Назад 🔙", callback_data="back"), InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
        elif language == "Azerbejani":
            change_language_button = InlineKeyboardButton("Dili dəyiş 🌐", callback_data="change_language")
            gender_interest_buttons = [InlineKeyboardButton("Cins 👤", callback_data="edit_gender"), InlineKeyboardButton("Marag ❤️", callback_data="edit_interest")]
            age_group_button = InlineKeyboardButton("Yaş qrupu 🎂", callback_data="edit_age_group")
            back_close_buttons = [InlineKeyboardButton("Geri 🔙", callback_data="back"), InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
        else:
            return

        new_reply_markup = InlineKeyboardMarkup([
            [change_language_button],
            gender_interest_buttons,
            [age_group_button],
            back_close_buttons
        ])

        # Edit the message with the new buttons
        callback_query.message.edit_reply_markup(reply_markup=new_reply_markup)
    except Exception as e:
        print("Error in edit_profile:", e)

    
@Client.on_callback_query(filters.regex("^change_language_"))
def change_language(client, callback_query):
    try:
        # Get the user ID and old language
        user_id = callback_query.from_user.id
        old_lang = find_language(user_id)

        # Define the buttons for available languages excluding the old language
        if old_lang == "English":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Русский 🇷🇺", callback_data="set_language_russian")],
                [InlineKeyboardButton("Azərbaycan 🇦🇿", callback_data="set_language_azerbaijani")],
                [InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
            caption = "Choose your new language 🌐"
        elif old_lang == "Russian":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("English 🇺🇸", callback_data="set_language_english")],
                [InlineKeyboardButton("Azərbaycan 🇦🇿", callback_data="set_language_azerbaijani")],
                [InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
            caption = "Выберите новый язык 🌐"
        elif old_lang == "Azerbejani":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("English 🇺🇸", callback_data="set_language_english")],
                [InlineKeyboardButton("Русский 🇷🇺", callback_data="set_language_russian")],
                [InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
            ])
            caption = "Yeni dilinizi seçin 🌐"
        else:
            return

        # Edit the message with the new language options
        callback_query.message.edit_caption(caption, reply_markup=reply_markup)
    except Exception as e:
        print("Error in change_language:", e)


# Callback function for setting the language
@Client.on_callback_query(filters.regex("^set_language_"))
def set_language(client, callback_query):
    try:
        # Extract the new language from the callback data
        new_lang = callback_query.data.split("_")[-1]

        # Get the user ID and old language
        user_id = callback_query.from_user.id
        old_lang = find_language(user_id)

        # Attempt to change the language
        if edit_language(user_id, old_lang, new_lang):
            # If language change is successful, inform the user
            callback_query.answer(f"Language changed to {new_lang} successfully!", show_alert=True)
            # Edit the message to display the success message in the new language
            if new_lang == "English":
                success_message = "Language changed successfully! 🇺🇸"
            elif new_lang == "Russian":
                success_message = "Язык успешно изменен! 🇷🇺"
            elif new_lang == "Azerbejani":
                success_message = "Dil uğurla dəyişdirildi! 🇦🇿"
            else:
                return
            callback_query.message.edit_text(success_message)
        else:
            # If language change fails, inform the user
            callback_query.answer("Failed to change language.", show_alert=True)

        # Delete the callback message
        callback_query.message.delete()
    except Exception as e:
        print("Error in set_language:", e)
