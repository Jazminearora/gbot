from pyrogram import filters
from zenova import zenova, BOT_USERNAME
from helpers.helper import get_profile, find_language, remove_user_id, add_user_id, get_interest, is_user_registered
from helpers.get_msg import get_interest_reply_markup, get_reply_markup, get_lang_change
from helpers.referdb import save_id, is_served_user, referral_count
from helpers.translator import translate_text
import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from pyrogram.enums import ParseMode

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
                    # Check if the sender user ID has already been referred
                    is_referred = await is_served_user(user_id)
                    print("served true")
                    if not is_referred:
                        # Check if the user is already registered
                        is_registered =  is_user_registered(user_id)
                        print("register false")
                        if not is_registered:
                            # Save the sender user ID as referred by the referer user ID
                            await save_id(referer_user_id, user_id)
                            print('saved')
                            await message.reply_text(f"You are successfully refered by {name}. \n\nPlease register now for using bot by command: /register")
                            referer_lang = find_language(referer_user_id)
                            referred_name = await get_user_name(user_id)
                            total_refer =await len(referral_count(referer_user_id))
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
button_pattern = re.compile(r"^🔧 (Configure search|Настроить поиск|Axtarışı tənzimlə) 🔧|👤 (Profile|Профиль|Profil) 👤|🔝 (Top|Лучшие|Ən yuxarı) 🔝|👥 (Add to group|Добавить в группу|Qrupa əlavə et) 👥|👫 (Friends|Друзья|Dostlar) 👫$")

@zenova.on_message(filters.private & filters.regex(button_pattern))
async def handle_keyboard_response(client, message):
    text = message.text
    if "Configure search" in text or "Настроить поиск" in text or "Axtarışı tənzimlə" in text:
        await message.reply_text("Configuring search...")
    elif "Profile" in text or "Профиль" in text or "Profil" in text:
        wait_message = await message.reply_text("💭")
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
        bot = BOT_USERNAME
        markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Add me to your group", url = f"https://t.me/{bot}?startgroup=true")]])
        await message.reply_text("Adding to group...", reply_markup = markup)
    elif "Friends" in text or "Друзья" in text or "Dostlar" in text:
        await message.reply_text("Viewing friends...")

@zenova.on_callback_query(filters.regex("^close_profile$"))
async def close_profile(client, callback_query):
    try:
        # Delete the callback message
        await callback_query.message.delete()
    except Exception as e:
        print("Error in close_profile:", e)

@zenova.on_callback_query(filters.regex("^back$"))
async def back(client, callback_query):
    try:
        user_id =callback_query.from_user.id
        language = find_language(user_id)
        profile_text, reply_markup = get_profile(user_id, language)
        try:
            await callback_query.message.edit_caption(profile_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        except Exception as e:
            await callback_query.message.edit_caption(f"An error occurred: {str(e)}")
    except Exception as e:
        await callback_query.message.edit_caption(f"An error occurred: {str(e)}")

@zenova.on_callback_query(filters.regex("^edit_profile$"))
async def edit_profile(client, callback_query):
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
        await callback_query.message.edit_reply_markup(reply_markup=new_reply_markup)
    except Exception as e:
        print("Error in edit_profile:", e)

    
@zenova.on_callback_query(filters.regex("^change_language"))
async def change_language(client, callback_query):
    try:
        # Get the user ID and old language
        user_id = callback_query.from_user.id
        old_lang = find_language(user_id)
        caption, reply_markup = get_lang_change(old_lang)
        # Edit the message with the new language options
        await callback_query.message.edit_caption(caption, reply_markup=reply_markup)
    except Exception as e:
        print("Error in change_language:", e)


# Callback function for setting the language
@zenova.on_callback_query(filters.regex("^set_language"))
async def set_language(client, callback_query):
    try:
        # Extract the new language from the callback data
        new_lang = callback_query.data.split("_")[2]
        print("new language:", new_lang)
        muks = await callback_query.message.edit_caption("🔍")
        # Get the user ID and old language
        user_id = callback_query.from_user.id
        old_lang = find_language(user_id)
        remove_user_id(old_lang, user_id, old_lang)
        trumk = await muks.edit_caption("🤖")
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
            print(success_message)
            await trumk.edit_caption(success_message, reply_markup=ReplyKeyboardRemove(selective= True))
        except Exception as e:
            print("Error in changing language:", e)

    except Exception as e:
        print("Error in set_language:", e)


@zenova.on_callback_query(filters.regex("^edit_interest$"))
async def edit_interest(client, callback_query):
    try:
        # Get the user ID and language
        user_id = callback_query.from_user.id
        language = find_language(user_id)
        print(language)

        # Fetch current interest
        current_interest = get_interest(user_id, language)

        # Get reply markup and caption
        reply_arkup, captoion = get_interest_reply_markup(current_interest, language)

        # Edit the message with the new interest options
        await callback_query.message.edit_caption(captoion, reply_markup=reply_arkup)

    except Exception as e:
        print("Error in edit_interest:", e)

@zenova.on_callback_query(filters.regex("^set_interest"))
async def set_interest(client, callback_query):
    try:
        language = find_language(user_id)
        new_interest = callback_query.data.split("_")[2]
        print("new interest:", new_interest)
        muks = await callback_query.message.edit_caption("🔍")
        # Get the user ID and old language
        user_id = callback_query.from_user.id
        old_interest = get_interest(user_id, language)
        remove_user_id(old_interest, user_id, old_interest)
        trumk = await muks.edit_caption("🤖")
        add_user_id(new_interest, user_id, new_interest)
        try:
            # If language change is successful, inform the user
            await callback_query.answer(f"↪️ {new_interest} ✅", show_alert=True)
            # Edit the message to display the success message in the new language
            if language == "English":
                success_message = "interest changed successfully!"
            elif language == "Russian":
                success_message = "интерес успешно изменился!"
            elif language == "Azerbejani":
                success_message = "maraq uğurla dəyişdi!"
            print(success_message)
            await trumk.edit_caption(success_message, reply_markup=ReplyKeyboardRemove(selective= True))
        except Exception as e:
            print("Error in changing language:", e)
    
    except Exception as e:
        print("Error in set_language:", e)