from pyrogram import filters, types
from zenova import zenova
from helpers.helper import get_profile, find_language
import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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

# Handle private messages with the reply markup
@zenova.on_message(filters.command(["start"]) & filters.private)
async def start_command(client, message):
    try:
        user_id = message.from_user.id
        language = find_language(user_id)
        reply_markup = get_reply_markup(language)
        await message.reply_text("Please select an option:", reply_markup=reply_markup)
    except Exception as e:
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
            await wait_message.edit_text(profile_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        except Exception as e:
            await wait_message.edit_text(f"An error occurred: {str(e)}")
    elif "Top" in text or "Лучшие" in text or "Ən yuxarı" in text:
        await message.reply_text("Viewing top options...")
    elif "Add to group" in text or "Добавить в группу" in text or "Qrupa əlavə et" in text:
        await message.reply_text("Adding to group...")
    elif "Friends" in text or "Друзья" in text or "Dostlar" in text:
        await message.reply_text("Viewing friends...")
