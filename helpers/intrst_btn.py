from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_interest_reply_markup(current_interest, language):
    if language == "English":
        if current_interest == "communication":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Intimacy 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Selling 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
        elif current_interest == "intimacy":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Communication 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Selling 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
        elif current_interest == "selling":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Communication 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Intimacy 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Close ❌", callback_data="close_profile")]
            ])
        caption = "Choose your new interest ❤️"
    elif language == "Russian":
        if current_interest == "communication":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Близость 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Продажи 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
        elif current_interest == "intimacy":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Общение 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Продажи 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
        elif current_interest == "selling":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Общение 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Близость 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Закрыть ❌", callback_data="close_profile")]
            ])
        caption = "Выберите новый интерес ❤️"
    elif language == "Azerbejani":
        if current_interest == "communication":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Yaxınlıq 💕", callback_data="set_interest_intimacy")],
                [InlineKeyboardButton("Satış 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
            ])
        elif current_interest == "intimacy":
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Əlaqə 👥", callback_data="set_interest_communication")],
                [InlineKeyboardButton("Satış 💰", callback_data="set_interest_selling")],
                [InlineKeyboardButton("Bağla ❌", callback_data="close_profile")]
            ])
        elif current_interest == "selling":
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