from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from helpers.helper import get_total_users
from helpers.translator import translate_async

async def get_age_markup(language):
    age_buttons = []
    # Add button for -15
    age_buttons.append(InlineKeyboardButton("-15", callback_data=f"register_age_{language}_-15"))
    # Create buttons for ages 15 to 34
    for age in range(16, 34):
        age_buttons.append(InlineKeyboardButton(str(age), callback_data=f"register_age_{language}_{age}"))
    
    # Add button for 35+
    age_buttons.append(InlineKeyboardButton("35+", callback_data=f"register_age_{language}_35+"))

    # Split buttons into rows of 5
    rows = [age_buttons[i:i+5] for i in range(0, len(age_buttons), 5)]
    
    return InlineKeyboardMarkup(rows)

# Registration message for register.py file
async def get_registration_text(language, step):
    age_markup = await get_age_markup(language)
    if language == "English":
        if step == "gender":
            return "Choose your gender:", InlineKeyboardMarkup([
                [InlineKeyboardButton("Male👦", callback_data=f"register_gender_{language}_male")],
                [InlineKeyboardButton("Female👧", callback_data=f"register_gender_{language}_female")]])
        elif step == "age":
            caption = f"""Welcome to the chat for anonymous communication ❤‍🔥

- look for new acquaintances
- communicate based on interests
- have fun 🤪
- 🔞Acquaintance (18+)

 👩🏼 online: {get_total_users("female")}
 🧑🏻 online: {get_total_users("male")}

Choose your gender """
            return caption , age_markup
        elif step == "interest":
            return "Choose your interest:", InlineKeyboardMarkup([
                [InlineKeyboardButton("👁‍🗨 Communication", callback_data=f"register_interest_{language}_communication")],
                [InlineKeyboardButton("🔞 Intimacy (18+)", callback_data=f"register_interest_{language}_intimacy")],
                [InlineKeyboardButton("🚼 Selling sex (18+)", callback_data=f"register_interest_{language}_selling")],
                [InlineKeyboardButton("🎬 Movies", callback_data=f"register_interest_{language}_movies")],
                [InlineKeyboardButton("🎌 Anime", callback_data=f"register_interest_{language}_anime")]])
        else:
            return None, None
    elif language == "Russian":
        if step == "gender":
            caption = f"""Добро пожаловать в чат для анонимного общения ❤‍🔥

- ищите новых знакомств
- общайтесь на основе интересов
- веселитесь 🤪
- 🔞Знакомства (18+)

 👩🏼 онлайн: {get_total_users("female")}
 🧑🏻 онлайн: {get_total_users("male")}

Выберите свой пол"""
            return caption , InlineKeyboardMarkup([
                [InlineKeyboardButton("Мужчина👦", callback_data=f"register_gender_{language}_male")],
                [InlineKeyboardButton("Женщина👧", callback_data=f"register_gender_{language}_female")]])
        elif step == "age":
            return "Выберите свою возрастную группу:", age_markup
        elif step == "interest":
            return "Выберите свой интерес:", InlineKeyboardMarkup([
                [InlineKeyboardButton("👁‍🗨 Коммуникация", callback_data=f"register_interest_{language}_communication")],
                [InlineKeyboardButton("🔞 Интимность (18+)", callback_data=f"register_interest_{language}_intimacy")],
                [InlineKeyboardButton("🚼 Продажа секса (18+)", callback_data=f"register_interest_{language}_selling")],
                [InlineKeyboardButton("🎬 Фильмы", callback_data=f"register_interest_{language}_movies")],
                [InlineKeyboardButton("🎌 Аниме", callback_data=f"register_interest_{language}_anime")]])
        else:
            return None, None

    elif language == "Azerbejani":
        if step == "gender":
            return "Cinsinizi seçin:", InlineKeyboardMarkup([
                [InlineKeyboardButton("Kişi👦", callback_data=f"register_gender_{language}_male")],
                [InlineKeyboardButton("Qadın👧", callback_data=f"register_gender_{language}_female")]])
        elif step == "age":
            caption = f"""Anonim kommunikasiya üçün söhbətə xoş gəlmisiniz ❤‍🔥

- yeni tanışlıqlar axtarın
- maraqlara əsasən kommunikasiya edin
- əylənəsiniz 🤪
- 🔞Tanışlıqlar (18+)

 👩🏼 onlayn: {get_total_users("female")}
 🧑🏻 onlayn: {get_total_users("male")}

Cinsinizi seçin """
            return caption , age_markup
        elif step == "interest":
            return "Maragınızı seçin:", InlineKeyboardMarkup([
                [InlineKeyboardButton("👁‍🗨 Kommunikasiya", callback_data=f"register_interest_{language}_communication")],
                [InlineKeyboardButton("🔞 Intim (18+)", callback_data=f"register_interest_{language}_intimacy")],
                [InlineKeyboardButton("🚼 Seks satışı (18+)", callback_data=f"register_interest_{language}_selling")],
                [InlineKeyboardButton("🎬 Filmlər", callback_data=f"register_interest_{language}_movies")],
                [InlineKeyboardButton("🎌 Anime", callback_data=f"register_interest_{language}_anime")]])
        else:
            return None, None
    else:
        return None, None


##================================================================================================##
##================================================================================================##


# Function to get reply markup with buttons in the user's selected language used in keyboard.py
async def get_reply_markup(language):
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
async def get_lang_change(old_lang):
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

async def get_interest_reply_markup(navigate: bool = None, language= None):
    if language == "English":
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Communication 👥", callback_data="set_interest_communication"),
             InlineKeyboardButton("Intimacy 💕", callback_data="set_interest_intimacy"),
             InlineKeyboardButton("Selling 💰", callback_data="set_interest_selling")],
            [InlineKeyboardButton("Movies 🎬", callback_data="set_interest_movies"),
             InlineKeyboardButton("Anime 🎌", callback_data="set_interest_anime"),
             InlineKeyboardButton("Music 🎵", callback_data="set_interest_music")],
            [InlineKeyboardButton("Gaming 🎮", callback_data="set_interest_gaming"),
             InlineKeyboardButton("Memes 🤣", callback_data="set_interest_memes"),
             InlineKeyboardButton("Relationships ❤️", callback_data="set_interest_relationships")],
            [InlineKeyboardButton("TikTok 🕺", callback_data="set_interest_tiktok"),
             InlineKeyboardButton("Flirting 😘", callback_data="set_interest_flirting"),
             InlineKeyboardButton("Travel 🌍", callback_data="set_interest_travel")],
            [InlineKeyboardButton("Study 📚", callback_data="set_interest_study"),
             InlineKeyboardButton("Food 🍔", callback_data="set_interest_food"),
             InlineKeyboardButton("Fitness 💪", callback_data="set_interest_fitness")],
            [InlineKeyboardButton("🔙", callback_data="back"),
             InlineKeyboardButton("❌", callback_data="close_profile")]
        ])
        caption = "Choose your interest ❤️"
    elif language == "Russian":
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Общение 👥", callback_data="set_interest_communication"),
             InlineKeyboardButton("Близость 💕", callback_data="set_interest_intimacy"),
             InlineKeyboardButton("Продажи 💰", callback_data="set_interest_selling")],
            [InlineKeyboardButton("Фильмы 🎬", callback_data="set_interest_movies"),
             InlineKeyboardButton("Аниме 🎌", callback_data="set_interest_anime"),
             InlineKeyboardButton("Музыка 🎵", callback_data="set_interest_music")],
            [InlineKeyboardButton("Игры 🎮", callback_data="set_interest_gaming"),
             InlineKeyboardButton("Мемы 🤣", callback_data="set_interest_memes"),
             InlineKeyboardButton("Отношения ❤️", callback_data="set_interest_relationships")],
            [InlineKeyboardButton("ТикТок 🕺", callback_data="set_interest_tiktok"),
             InlineKeyboardButton("Флирт 😘", callback_data="set_interest_flirting"),
             InlineKeyboardButton("Путешествия 🌍", callback_data="set_interest_travel")],
            [InlineKeyboardButton("Учеба 📚", callback_data="set_interest_study"),
             InlineKeyboardButton("Еда 🍔", callback_data="set_interest_food"),
             InlineKeyboardButton("Фитнес 💪", callback_data="set_interest_fitness")],
            [InlineKeyboardButton("🔙", callback_data="back"),
             InlineKeyboardButton("❌", callback_data="close_profile")]
        ])
        caption = "Выберите ваш интерес ❤️"
    elif language == "Azerbejani":
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Ünsiyyət 👥", callback_data="set_interest_communication"),
             InlineKeyboardButton("Yaxınlıq 💕", callback_data="set_interest_intimacy"),
             InlineKeyboardButton("Satış 💰", callback_data="set_interest_selling")],
            [InlineKeyboardButton("Filmlər 🎬", callback_data="set_interest_movies"),
             InlineKeyboardButton("Anime 🎌", callback_data="set_interest_anime"),
             InlineKeyboardButton("Musiqi 🎵", callback_data="set_interest_music")],
            [InlineKeyboardButton("Oyunlar 🎮", callback_data="set_interest_gaming"),
             InlineKeyboardButton("Meme-lər 🤣", callback_data="set_interest_memes"),
             InlineKeyboardButton("Münasibətlər ❤️", callback_data="set_interest_relationships")],
            [InlineKeyboardButton("TikTok 🕺", callback_data="set_interest_tiktok"),
             InlineKeyboardButton("Flirt 😘", callback_data="set_interest_flirting"),
             InlineKeyboardButton("Səyahət 🌍", callback_data="set_interest_travel")],
            [InlineKeyboardButton("Təhsil 📚", callback_data="set_interest_study"),
             InlineKeyboardButton("Yemək 🍔", callback_data="set_interest_food"),
             InlineKeyboardButton("Fitness 💪", callback_data="set_interest_fitness")],
            [InlineKeyboardButton("🔙", callback_data="back"),
             InlineKeyboardButton("❌", callback_data="close_profile")]
        ])
        caption = "Marağınızı seçin ❤️"
    
    return reply_markup, caption

async def get_configuration_room(lang):
    buttons = [
        [
            InlineKeyboardButton(text=await translate_async("Free Chat 💬", lang), callback_data="config_Free Chat"),
            InlineKeyboardButton(text=await translate_async("Flirting 💞", lang), callback_data="config_Flirting"),
            InlineKeyboardButton(text=await translate_async("Study Room 📚", lang), callback_data="config_Study Room"),
        ],
        [
            InlineKeyboardButton(text=await translate_async("Voice Chat 🎙️", lang), callback_data="config_Voice Chat"),
            InlineKeyboardButton(text=await translate_async("Movies 🎬", lang), callback_data="config_Movies"),
            InlineKeyboardButton(text=await translate_async("Games 🎮", lang), callback_data="config_Games"),
        ],
        [
            InlineKeyboardButton(text=await translate_async("Hobby 🎨", lang), callback_data="config_Hobby"),
            InlineKeyboardButton(text=await translate_async("Sport 🏅", lang), callback_data="config_Sport"),
            InlineKeyboardButton(text=await translate_async("Music 🎵", lang), callback_data="config_Music"),
        ],
        [
            InlineKeyboardButton(text=await translate_async("General ✅", lang), callback_data="configu_Genral"),
            InlineKeyboardButton(text=await translate_async("Back 🔙", lang), callback_data="cgoback"),
        ],
    ]

    return InlineKeyboardMarkup(buttons)

async def get_premium_msg(language):
    if language == "English":
        caption = "💎 PREMIUM\n⛔ Premium search is available only for VIP users ⛔\n\n🔞 Chat in dirty chat\n🔍 Search by gender (m/f)\n🎥 Share photos and videos\n🔥 Send photos, videos, GIFs, stickers\n📃 Information about the interlocutor (age)\n🚫 No advertising\n\n/referals - get 👑VIP for free"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("For a day - $1.08", callback_data="premium_1_day")],
            [InlineKeyboardButton("For a three days - $2.15", callback_data="premium_3_days")],
            [InlineKeyboardButton("For a week - $8.61", callback_data="premium_1_week")],
            [InlineKeyboardButton("For a month - $12.98", callback_data="premium_1_month")],
            [InlineKeyboardButton("Get it for free", callback_data="prem_free")]
        ])
    elif language == "Russian":
        caption = "💎 PREMIUM\n⛔ Премиум-поиск доступен только для пользователей VIP ⛔\n\n🔞 Чат в грязном чате\n🔍 Поиск по полу (м/ж)\n🎥 Обмен фотографиями и видео\n🔥 Отправка фотографий, видео, GIF, стикеров\n📃 Информация о собеседнике (возраст)\n🚫 Без рекламы\n\n/referals - получите 👑VIP бесплатно"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("На день - 81₽", callback_data="premium_1_day")],
            [InlineKeyboardButton("На три дня - 162₽", callback_data="premium_3_days")],
            [InlineKeyboardButton("На неделю - 648₽", callback_data="premium_1_week")],
            [InlineKeyboardButton("На месяц - 974₽", callback_data="premium_1_month")],
            [InlineKeyboardButton("Получить бесплатно", callback_data="prem_free")]
        ])
    elif language == "Azerbejani":
        caption = "💎 PREMIUM\n⛔ Premium axtarışı yalnız VIP istifadəçilər üçün mövcuddur ⛔\n\n🔞 Pis çatda söhbət edin\n🔍 Cinsiyətə görə axtarış (k/q)\n🎥 Şəkilləri və videoları paylaşın\n🔥 Şəkillər, videolar, GIF-lər, stikerlər göndərin\n📃 Müşahidəçi haqqında məlumat (yaş)\n🚫 Reklam yoxdur\n\n/referals - pulsuz 👑VIP alın"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Bir gün üçün - 1,08 $", callback_data="premium_1_day")],
            [InlineKeyboardButton("Üç gün üçün - 2,15 $", callback_data="premium_3_days")],
            [InlineKeyboardButton("Bir həftə üçün - 8,61 $", callback_data="premium_1_week")],
            [InlineKeyboardButton("Bir ay üçün - 12,98 $", callback_data="premium_1_month")],
            [InlineKeyboardButton("Pulsuz əldə edin", callback_data="prem_free")]
        ])
    else:
        caption = "Invalid language specified."
        buttons = InlineKeyboardMarkup([])
    return caption, buttons

async def interlocutor_vip_message(language, name, gender, age_group, verify_status):
    # Cool emojis and formatting
    interlocutor_found = await translate_async("""
🌟 Interlocutor found! 🌟

📋 User's details:
🔹 Name: """, language)
    
    details_and_chatting = await translate_async(f"""
🔹 Gender: {gender}
🔹 Age group: {age_group}
✅ Verified: {verify_status}

💬 You can start chatting now.""", language)
    
    message = f"{interlocutor_found}{name}\n{details_and_chatting}"
    return message



async def interlocutor_normal_message(language, verify_status):
    # Full message with placeholders and emojis
    message_template = f"""
🎉 Interlocutor found! 🎉

📋 User's details:
🔹 Name: 🔒🔒🔒
🔹 Gender:🔒🔒🔒
🔹 Age group: 🔒🔒🔒
✅ Verified: {verify_status}

🌟 Purchase Premium to know the details of the Interlocutor 😈!

💬 You can start chatting now.
    """
    
    # Translate the entire message template
    translated_message = await translate_async(message_template, language)
    
    return translated_message



def get_points_text(lang):
    if lang == "English":
        return "points"
    elif lang == "Russian":
        return "баллов"
    elif lang == "Azerbejani":
        return "nökbələri"

def get_top_text(lang):
    if lang == "English":
        return "Top Referers"
    elif lang == "Russian":
        return "Лучшие Рефералы"
    elif lang == "Azerbejani":
        return "Ən yaxşı referans verənlər"

def get_prize_text(lang):
    if lang == "English":
        return "Top referers get additional prizes like premium membership for free!"
    elif lang == "Russian":
        return "Лучшие рефералы получают дополнительные призы, такие как премиум-подписка бесплатно!"
    elif lang == "Azerbejani":
        return "Ən yaxşı referans verənlər premium üyvlİğİn daha ətraflı məlumatları üçün heç bir qiymətə qəbul edə bilərlər!"

def get_no_referers_text(lang):
    if lang == "English":
        return "There are no top referers yet. Keep inviting your friends to get rewards!"
    elif lang == "Russian":
        return "Пока нет лучших рефералов. Продолжайте приглашать своих друзей, чтобы получать награды!"
    elif lang == "Azerbejani":
        return "İndiyorlar mövcuddur. Dostlarınızı davam etmək üçün davet edin. Ödüllər almaq üçün!"