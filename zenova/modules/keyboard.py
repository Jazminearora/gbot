from pyrogram import filters, types
from zenova import zenova
from helpers.helper import get_profile, find_language, remove_user_id, add_user_id, get_interest, is_user_registered
from helpers.intrst_btn import get_interest_reply_markup
from helpers.referdb import save_id, is_served_user, referral_count
from helpers.translator import translate_text
import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from pyrogram.enums import ParseMode

# Function to get reply markup with buttons in the user's selected language
def get_reply_markup(language):
    if language == "English":
        # English buttons
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="🔍 Search for an interlocutor 🔎"),
                ],
                [
                    types.KeyboardButton(text="💎 Premium 💎"),
                    types.KeyboardButton(text="🔧 Configure search 🔧")
                ],
                [
                    types.KeyboardButton(text="👤 Profile 👤"),
                    types.KeyboardButton(text="🔝 Top 🔝")
                ],
                [
                    types.KeyboardButton(text="👥 Add to group 👥"),
                    types.KeyboardButton(text="👫 Friends 👫")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    elif language == "Russian":
        # Russian buttons
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="🔍 Найти собеседника 🔎"),
                ],
                [
                    types.KeyboardButton(text="💎 Премиум 💎"),
                    types.KeyboardButton(text="🔧 Настроить поиск 🔧")
                ],
                [
                    types.KeyboardButton(text="👤 Профиль 👤"),
                    types.KeyboardButton(text="🔝 Лучшие 🔝")
                ],
                [
                    types.KeyboardButton(text="👥 Добавить в группу 👥"),
                    types.KeyboardButton(text="👫 Друзья 👫")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    elif language == "Azerbejani":
        # Azerbaijani buttons
        reply_markup = types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="🔍 Məqalə axtar 🔎"),
                ],
                [
                    types.KeyboardButton(text="💎 Premium 💎"),
                    types.KeyboardButton(text="🔧 Axtarışı tənzimlə 🔧")
                ],
                [
                    types.KeyboardButton(text="👤 Profil 👤"),
                    types.KeyboardButton(text="🔝 Ən yuxarı 🔝")
                ],
                [
                    types.KeyboardButton(text="👥 Qrupa əlavə et 👥"),
                    types.KeyboardButton(text="👫 Dostlar 👫")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    # Add more languages as needed
    return reply_markup

async def get_user_name(user_id):
    try:
        user = await zenova.get_users(user_id)
        if user:
            name = user.first_name
            if user.last_name:
                name += " " + user.last_name
            return name
    except Exception as e:
        return None

# Handle private messages with the reply markup
@zenova.on_message(filters.command(["start"]) & filters.private)
async def start_command(client, message):
    # Extract the referer user id from the command message
    command_parts = message.text.split(" ")
    if len(command_parts) > 1:
        try:
            referer_user_id = int(command_parts[1].replace("r", ""))
            print("referer id = ", referer_user_id)
        except ValueError:
            await message.reply("Invalid referer user id format. Use 'start=r{user_id}'")
            return
        name = await get_user_name(referer_user_id)
        if name is not None:
            try:
                user_id = message.from_user.id
                if command_parts:
                    referer_user_id = int(command_parts[1].replace("r", ""))
                    # Check if the sender user ID has already been referred
                    is_referred = is_served_user(user_id)
                    print("served true")
                    if not is_referred:
                        # Check if the user is already registered
                        is_registered = await is_user_registered(user_id)
                        print("register false")
                        if not is_registered:
                            # Save the sender user ID as referred by the referer user ID
                            await save_id(referer_user_id, user_id)
                            print('saved')
                            await message.reply_text(f"You are successfully refered by {name}. \n\nPlease register now for using bot by command: /register")
                            referer_lang = find_language(referer_user_id)
                            referred_name = await get_user_name(user_id)
                            total_refer = referral_count(referer_user_id)
                            caption = f"You have successfully referred to {referred_name}.\n\n Total refers: {total_refer}"
                            if referer_lang == "English":
                                await zenova.send_message(referer_user_id, caption)
                            elif referer_lang == "Russian":
                                await zenova.send_message(referer_user_id, translate_text(caption, target_language="ru"))
                            elif referer_lang == "Azerbejani":
                                await zenova.send_message(referer_user_id, translate_text(caption, target_language="az"))
                            zenova.send_message(referer_user_id, caption)
                        else:
                            await message.reply_text("You are Already registered!")
                    else:
                        await message.reply_text("You are already refered by someone!")
            except Exception as e:
                await message.reply_text(f"An error occurred: {str(e)}")
        else:
            await message.reply_text(f"Referer id {referer_user_id} is invalid.")
    try:
        user_id = message.from_user.id
        language = find_language(user_id)
        reply_markup = get_reply_markup(language)
        await message.reply_text("Please select an option:", reply_markup=reply_markup)
    except Exception:
        await message.reply_text("It seems you haven't registered yet! Please register first using /register.")


# Define a regex pattern to match the button texts for all three languages
button_pattern = re.compile(r"^(🔍 (Search for an interlocutor|Найти собеседника|Məqalə axtar) 🔎|💎 (Premium|Премиум|Premium) 💎|🔧 (Configure search|Настроить поиск|Axtarışı tənzimlə) 🔧|👤 (Profile|Профиль|Profil) 👤|🔝 (Top|Лучшие|Ən yuxarı) 🔝|👥 (Add to group|Добавить в группу|Qrupa əlavə et) 👥|👫 (Friends|Друзья|Dostlar) 👫)$")

@zenova.on_message(filters.private & filters.regex(button_pattern))
async def handle_keyboard_response(client, message):
    text = message.text
    if "Search for an interlocutor" in text or "Найти собеседника" in text or "Məqalə axtar" in text:
        await message.reply_text("Searching for an interlocutor...")
    elif "Premium" in text or "Премиум" in text or "Premium" in text:
        await message.reply_text("You selected Premium option.")
    elif "Configure search" in text or "Настроить поиск" in text or "Axtarışı tənzimlə" in text:
        await message.reply_text("Configuring search...")
    elif "Profile" in text or "Профиль" in text or "Profil" in text:
        wait_message = await message.reply_text("Please wait, Fetching details...")
        try:
            user_id = message.from_user.id
            language = find_language(user_id)
            profile_text, reply_markup = get_profile(user_id, language)
            try:
                await wait_message.edit_text(profile_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            except Exception as e:
                await wait_message.edit_text(f"An error occurred: {str(e)}")
        except Exception as e:
            await wait_message.edit_text(f"An error occurred: {str(e)}")
    elif "Top" in text or "Лучшие" in text or "Ən yuxarı" in text:
        await message.reply_text("Viewing top options...")
    elif "Add to group" in text or "Добавить в группу" in text or "Qrupa əlavə et" in text:
        await message.reply_text("Adding to group...")
    elif "Friends" in text or "Друзья" in text or "Dostlar" in text:
        await message.reply_text("Viewing friends...")



@zenova.on_callback_query(filters.regex("^close_profile$"))
def close_profile(client, callback_query):
    try:
        # Delete the callback message
        callback_query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

@zenova.on_callback_query(filters.regex("^edit_profile$"))
def edit_profile(client, callback_query):
    try:
        # Get the user ID and language
        user_id = callback_query.from_user.id
        language = find_language(user_id)

        # Create the reply markup with the new buttons
        if language == "English":
            change_language_button = InlineKeyboardButton("Change language 🌐", callback_data="change_language")
            interest_button = InlineKeyboardButton("Change Interest ❤️", callback_data="edit_interest")
            back_close_buttons = [InlineKeyboardButton("Back 🔙", callback_data="back"), InlineKeyboardButton("Close ❌", callback_data="close_profile")]
        elif language == "Russian":
            change_language_button = InlineKeyboardButton("Изменить язык 🌐", callback_data="change_language")
            interest_button = InlineKeyboardButton("Изменить интерес ❤️", callback_data="edit_interest")
            back_close_buttons = [InlineKeyboardButton("Назад 🔙", callback_data="back"), InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
        elif language == "Azerbejani":
            change_language_button = InlineKeyboardButton("Dili dəyiş 🌐", callback_data="change_language")
            interest_button = InlineKeyboardButton("Maragı dəyiş ❤️", callback_data="edit_interest")
            back_close_buttons = [InlineKeyboardButton("Geri 🔙", callback_data="back"), InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
        else:
            return


        new_reply_markup = InlineKeyboardMarkup([
            [change_language_button],
            [interest_button],
            back_close_buttons
        ])

        # Edit the message with the new buttons
        callback_query.message.edit_reply_markup(reply_markup=new_reply_markup)
    except Exception as e:
        print("Error in edit_profile:", e)

    
@zenova.on_callback_query(filters.regex("^change_language"))
def change_language(client, callback_query):
    try:
        # Get the user ID and old language
        user_id = callback_query.from_user.id
        old_lang = find_language(user_id)

        # Define the buttons for available languages excluding the old language
        if old_lang == "English":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Русский 🇷🇺", callback_data="set_language_Russian")],
                [InlineKeyboardButton("Azərbaycan 🇦🇿", callback_data="set_language_Azerbejani")],
                [InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
            caption = "Choose your new language 🌐"
        elif old_lang == "Russian":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("English 🇺🇸", callback_data="set_language_English")],
                [InlineKeyboardButton("Azərbaycan 🇦🇿", callback_data="set_language_Azerbejani")],
                [InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
            caption = "Выберите новый язык 🌐"
        elif old_lang == "Azerbejani":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("English 🇺🇸", callback_data="set_language_English")],
                [InlineKeyboardButton("Русский 🇷🇺", callback_data="set_language_Russian")],
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
@zenova.on_callback_query(filters.regex("^set_language"))
def set_language(client, callback_query):
    try:
        # Extract the new language from the callback data
        new_lang = callback_query.data.split("_")[2]
        print("new language:", new_lang)
        muks = callback_query.message.edit_caption("🔍")
        # Get the user ID and old language
        user_id = callback_query.from_user.id
        old_lang = find_language(user_id)
        huks = muks.edit_caption("⚙️")
        remove_user_id(old_lang, user_id, old_lang)
        trumk = huks.edit_caption("🤖")
        add_user_id(new_lang, user_id, new_lang)


        try:
            # If language change is successful, inform the user
            callback_query.answer(f"Language changed to {new_lang} successfully!", show_alert=True)
            # Edit the message to display the success message in the new language
            if new_lang == "English":
                success_message = "Language changed successfully! 🇺🇸"
            elif new_lang == "Russian":
                success_message = "Язык успешно изменен! 🇷🇺"
            elif new_lang == "Azerbejani":
                success_message = "Dil uğurla dəyişdirildi! 🇦🇿"
            print(success_message)
            trumk.edit_caption(success_message, reply_markup=ReplyKeyboardRemove(selective= True))
        except Exception as e:
            print("Error in changing language:", e)

    except Exception as e:
        print("Error in set_language:", e)


@zenova.on_callback_query(filters.regex("^edit_interest$"))
def edit_interest(client, callback_query):
    try:
        # Get the user ID and language
        user_id = callback_query.from_user.id
        language = find_language(user_id)
        print(language)

        # Fetch current interest
        current_interest = get_interest(user_id, language)

        # Get reply markup and caption
        reply_arkup, captoion = get_interest_reply_markup(current_interest, language)
        print(reply_arkup)

        # Edit the message with the new interest options
        callback_query.message.edit_caption(captoion, reply_markup=reply_arkup)

    except Exception as e:
        print("Error in edit_interest:", e)