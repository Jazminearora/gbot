from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# Registration message for register.py file
def get_registration_text(language, step):
    if language == "English":
        if step == "gender":
            return "Choose your gender:", InlineKeyboardMarkup([
                [InlineKeyboardButton("Male👦", callback_data=f"register_gender_{language}_male")],
                [InlineKeyboardButton("Female👧", callback_data=f"register_gender_{language}_female")]])
        elif step == "age":
            return "Choose your age group:", InlineKeyboardMarkup([
                [InlineKeyboardButton("Below 18", callback_data=f"register_age_{language}_below-18")],
                [InlineKeyboardButton("18-24", callback_data=f"register_age_{language}_18-24")],
                [InlineKeyboardButton("25-34", callback_data=f"register_age_{language}_25-34")],
                [InlineKeyboardButton("Above 35", callback_data=f"register_age_{language}_above-35")]])
        elif step == "interest":
            return "Choose your interest:", InlineKeyboardMarkup([
                [InlineKeyboardButton("👁‍🗨 Communication", callback_data=f"register_interest_{language}_communication")],
                [InlineKeyboardButton("🔞 Intimacy (18+)", callback_data=f"register_interest_{language}_intimacy")],
                [InlineKeyboardButton("🚼 Selling sex (18+)", callback_data=f"register_interest_{language}_selling")]])
        else:
            return None, None
    elif language in ["Russian", "Azerbejani"]:
        if step == "gender":
            return "Выберите свой пол:", InlineKeyboardMarkup([
                [InlineKeyboardButton("Мужчина👦", callback_data=f"register_gender_{language}_male")],
                [InlineKeyboardButton("Женщина👧", callback_data=f"register_gender_{language}_female")]])
        elif step == "age":
            return "Выберите свою возрастную группу:", InlineKeyboardMarkup([
                [InlineKeyboardButton("Младше 18", callback_data=f"register_age_{language}_below-18")],
                [InlineKeyboardButton("18-24", callback_data=f"register_age_{language}_18-24")],
                [InlineKeyboardButton("25-34", callback_data=f"register_age_{language}_25-34")],
                [InlineKeyboardButton("Старше 35", callback_data=f"register_age_{language}_above-35")]])
        elif step == "interest":
            return "Выберите свой интерес:", InlineKeyboardMarkup([
                [InlineKeyboardButton("👁‍🗨 Коммуникация", callback_data=f"register_interest_{language}_communication")],
                [InlineKeyboardButton("🔞 Интимность (18+)", callback_data=f"register_interest_{language}_intimacy")],
                [InlineKeyboardButton("🚼 Продажа секса (18+)", callback_data=f"register_interest_{language}_selling")]])
        else:
            return None, None
    else:
        return None, None
    

# Function to get reply markup with buttons in the user's selected language used in keyboard.py
def get_reply_markup(language):
    if language == "English":
        # English buttons
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🔍 Search for an interlocutor 🔎"),
                ],
                [
                    KeyboardButton(text="💎 Premium 💎"),
                    KeyboardButton(text="🔧 Configure search 🔧")
                ],
                [
                    KeyboardButton(text="👤 Profile 👤"),
                    KeyboardButton(text="🔝 Top 🔝")
                ],
                [
                    KeyboardButton(text="👥 Add to group 👥"),
                    KeyboardButton(text="👫 Friends 👫")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    elif language == "Russian":
        # Russian buttons
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🔍 Найти собеседника 🔎"),
                ],
                [
                    KeyboardButton(text="💎 Премиум 💎"),
                    KeyboardButton(text="🔧 Настроить поиск 🔧")
                ],
                [
                    KeyboardButton(text="👤 Профиль 👤"),
                    KeyboardButton(text="🔝 Лучшие 🔝")
                ],
                [
                    KeyboardButton(text="👥 Добавить в группу 👥"),
                    KeyboardButton(text="👫 Друзья 👫")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    elif language == "Azerbejani":
        # Azerbaijani buttons
        reply_markup = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="🔍 Məqalə axtar 🔎"),
                ],
                [
                    KeyboardButton(text="💎 Premium 💎"),
                    KeyboardButton(text="🔧 Axtarışı tənzimlə 🔧")
                ],
                [
                    KeyboardButton(text="👤 Profil 👤"),
                    KeyboardButton(text="🔝 Ən yuxarı 🔝")
                ],
                [
                    KeyboardButton(text="👥 Qrupa əlavə et 👥"),
                    KeyboardButton(text="👫 Dostlar 👫")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    # Add more languages as needed
    return reply_markup

# function to get language change messae used in keyboard.py
def get_lang_change(old_lang):
    if old_lang == "English":
        reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Русский 🇷🇺", callback_data="set_language_Russian")],
                [InlineKeyboardButton("Azərbaycan 🇦🇿", callback_data="set_language_Azerbejani")],
                [InlineKeyboardButton("Back 🔙", callback_data="back"), InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
        caption = "Choose your new language 🌐"
    elif old_lang == "Russian":
        reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("English 🇺🇸", callback_data="set_language_English")],
                [InlineKeyboardButton("Azərbaycan 🇦🇿", callback_data="set_language_Azerbejani")],
                [InlineKeyboardButton("Назад 🔙", callback_data="back"), InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
        caption = "Выберите новый язык 🌐"
    elif old_lang == "Azerbejani":
        reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("English 🇺🇸", callback_data="set_language_English")],
                [InlineKeyboardButton("Русский 🇷🇺", callback_data="set_language_Russian")],
                [InlineKeyboardButton("Geri 🔙", callback_data="back"), InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
            ])
        caption = "Yeni dilinizi seçin 🌐"
    return caption, reply_markup
    

# function to get interest change messae used in keyboard.py
def get_interest_reply_markup(current_interest, language):
    print(current_interest)
    if language == "English":
        if current_interest == "Communication":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Intimacy 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Selling 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
        elif current_interest == "Intimacy":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Communication 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Selling 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
        elif current_interest == "Selling":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Communication 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Intimacy 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
        caption = "Choose your new interest ❤️"
    elif language == "Russian":
        if current_interest == "Communication":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Близость 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Продажи 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
        elif current_interest == "Intimacy":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Общение 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Продажи 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
        elif current_interest == "Selling":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Общение 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Близость 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
        caption = "Выберите новый интерес ❤️"
    elif language == "Azerbejani":
        if current_interest == "Communication":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Yaxınlıq 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Satış 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
            ])
        elif current_interest == "Intimacy":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Əlaqə 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Satış 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
            ])
        elif current_interest == "Selling":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Əlaqə 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Yaxınlıq 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
            ])
        caption = "Yeni marağınızı seçin ❤️"
    else:
        reply_markup = None
        caption = None

    return reply_markup, caption

async def get_premium_msg(language):
    if language == "English":
        caption = "💎 PREMIUM\n⛔ Premium search is available only for VIP users ⛔\n\n🔞 Chat in dirty chat\n🔍 Search by gender (m/f)\n🎥 Share photos and videos\n🔥 Send photos, videos, GIFs, stickers\n📃 Information about the interlocutor (age)\n🚫 No advertising\n\n/referals - get 👑VIP for free"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("For a day - $1.08", callback_data="premium_1_day")],
            [InlineKeyboardButton("For a three days - $2.15", callback_data="premium_3_days")],
            [InlineKeyboardButton("For a week - $8.61", callback_data="premium_1_week")],
            [InlineKeyboardButton("For a month - $12.98", callback_data="premium_1_month")],
            [InlineKeyboardButton("Get it for free", callback_data="premium_free")]
        ])
    elif language == "Russian":
        caption = "💎 PREMIUM\n⛔ Премиум-поиск доступен только для пользователей VIP ⛔\n\n🔞 Чат в грязном чате\n🔍 Поиск по полу (м/ж)\n🎥 Обмен фотографиями и видео\n🔥 Отправка фотографий, видео, GIF, стикеров\n📃 Информация о собеседнике (возраст)\n🚫 Без рекламы\n\n/referals - получите 👑VIP бесплатно"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("На день - 81₽", callback_data="premium_1_day")],
            [InlineKeyboardButton("На три дня - 162₽", callback_data="premium_3_days")],
            [InlineKeyboardButton("На неделю - 648₽", callback_data="premium_1_week")],
            [InlineKeyboardButton("На месяц - 974₽", callback_data="premium_1_month")],
            [InlineKeyboardButton("Получить бесплатно", callback_data="premium_free")]
        ])
    elif language == "Azerbejani":
        caption = "💎 PREMIUM\n⛔ Premium axtarışı yalnız VIP istifadəçilər üçün mövcuddur ⛔\n\n🔞 Pis çatda söhbət edin\n🔍 Cinsiyətə görə axtarış (k/q)\n🎥 Şəkilləri və videoları paylaşın\n🔥 Şəkillər, videolar, GIF-lər, stikerlər göndərin\n📃 Müşahidəçi haqqında məlumat (yaş)\n🚫 Reklam yoxdur\n\n/referals - pulsuz 👑VIP alın"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Bir gün üçün - 1,08 $", callback_data="premium_1_day")],
            [InlineKeyboardButton("Üç gün üçün - 2,15 $", callback_data="premium_3_days")],
            [InlineKeyboardButton("Bir həftə üçün - 8,61 $", callback_data="premium_1_week")],
            [InlineKeyboardButton("Bir ay üçün - 12,98 $", callback_data="premium_1_month")],
            [InlineKeyboardButton("Pulsuz əldə edin", callback_data="premium_free")]
        ])
    else:
        caption = "Invalid language specified."
        buttons = InlineKeyboardMarkup([])
    return caption, buttons