from Modules import mongodb as collection, BOT_USERNAME
from langdb.profile import text_1, text_2, text_3
from config import key
from helpers.translator import translate_text, translate_async
from database.premiumdb import is_user_premium, calculate_remaining_time, vip_users_details
from database.chatdb import users_rating_details, users_chat_details
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def find_language(user_id):
    stored_data = collection.find_one({key: {"$exists": True}})
    if stored_data:
        for language, lang_data in stored_data[key]["database"].items():
            if language in ["English", "Russian", "Azerbejani"] and user_id in lang_data:
                return language
    return None

def get_total_users(field):
    try:
        total_users = 0
        document = collection.find_one({key: {"$exists": True}})
        if document and field in document[key]["database"]:
            lang_data = document[key]["database"][field]
            total_users += len(lang_data)  
        return total_users
    except Exception as e:
        print(f'Error in getting total users for {field}:', e)
        return None

def get_users_list(language):
    try:
        users_list = []
        document = collection.find_one({key: {"$exists": True}})
        if document and language in document[key]["database"]:
            lang_data = document[key]["database"][language]
            users_list = [user_id for user_id in lang_data]
        return users_list
    except Exception as e:
        print(f'Error in getting users list for {language}:', e)
        return None
    
    
def get_gender(user_id, language):
    try:
        document = collection.find_one({key: {'$exists': True}})
        if document:
            lang_data = document[key]['database']
            if "male" in lang_data and str(user_id) in lang_data["male"]:
                return "male"
            elif "female" in lang_data and str(user_id) in lang_data["female"]:
                return "female"
    except Exception as e:
        print('Exception occurred in get_gender:', e)
    return None

def get_age_group(user_id, language):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document:
            lang_data = document[key]["database"]
            for age_group in ["below_18", "18_24", "25_34", "above_35"]:
                if str(user_id) in lang_data.get(age_group, []):
                    return age_group.replace("_", "-").capitalize()
    except Exception as e:
        print('Exception occurred in get_age_group:', e)
    return None

def get_interest(user_id, _):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document:
            lang_data = document[key]["database"]
            for interest in ["communication", "intimacy", "selling", "movies", "anime"]:
                if str(user_id) in lang_data.get(interest, []):
                    return interest.capitalize()
    except Exception as e:
        print('Exception occurred in get_interest:', e)
    return None

    
def is_user_registered(user_id):
    language = find_language(user_id)
    if language:
        gender = get_gender(user_id, language)
        age_group = get_age_group(user_id, language)
        interest = get_interest(user_id, language)
        if gender and age_group and interest:
            return True
        else:
            return False
    else:    
        return False

def get_detailed_user_list(language):
    try:
        detailed_list = {}
        users_list = get_users_list(language)
        print(users_list)
        if users_list:
            detailed_list["Total Users"] = len(users_list)
            detailed_list["Gender"] = {}
            detailed_list["Age Group"] = {}
            detailed_list["Interest"] = {}
            
            for user_id in users_list:
                gender = get_gender(user_id, language)
                age_group = get_age_group(user_id, language)
                interest = get_interest(user_id, language)
                if gender:
                    detailed_list["Gender"][gender] = detailed_list["Gender"].get(gender, 0) + 1
                if age_group:
                    detailed_list["Age Group"][age_group] = detailed_list["Age Group"].get(age_group, 0) + 1
                if interest:
                    detailed_list["Interest"][interest] = detailed_list["Interest"].get(interest, 0) + 1
            
            return detailed_list
        else:
            return None
    except Exception as e:
        print(f'Error in getting detailed user list for {language}:', e)
        return None
    

# async def get_profile(user_id, language):
#     premium, time = is_user_premium(str(user_id))
#     if premium:
#         expiry = calculate_remaining_time(time)
#     try:
#         gender = get_gender(user_id, language)
#         age_group = get_age_group(user_id, language)
#         interest = get_interest(user_id, language)
#         chat_details = users_rating_details(user_id, "rating")
#         total_msg = users_chat_details(user_id, "total_message")
#         dialogs = vip_users_details(user_id, "total_dialog")
#         rating = str(chat_details).replace("{", "").replace("}", "").replace("'", "").replace(",", "")
#         offense = users_chat_details(user_id, "profanity_score")
#         if language == "English":
#             message = text_1.format(gender=gender, age_group=age_group, interest=interest)
#             message += f"\nPremium Status: {premium}"
#             if premium:
#                 message += f"\nPremium Expiry: {expiry}"
#             message += "\n" + rating
#             message += f"\n\nTotal messages sent: {total_msg}\n Total dialogs: {dialogs}"
#             message += f"\n\n🔞 Offense Count: {offense}"
#             edit_button_text = "Edit ✏️"
#             close_button_text = "Close ❌"
#         elif language == "Russian":
#             ru_gender = translate_text(gender, target_language="ru")
#             ru_age_group = translate_text(age_group, target_language="ru")
#             ru_interest = translate_text(interest, target_language="ru")
#             message = text_2.format(gender=ru_gender, age_group=ru_age_group, interest=ru_interest)
#             message += f"\nСтатус премиума: {premium}"
#             if premium:
#                 message += f"\nСрок действия премиума: {expiry}"
#             message += f"\n\nОбщее количество отправленных сообщений: {total_msg}\nОбщее количество диалогов: {dialogs}"
#             message += f"\n\n🔞 Количество нарушений: {offense}"
#             edit_button_text = "Редактировать ✏️"
#             close_button_text = "Закрыть ❌"
#         elif language == "Azerbejani":
#             az_gender = translate_text(gender, target_language="az")
#             az_age_group = translate_text(age_group, target_language="az")
#             az_interest = translate_text(interest, target_language="az")
#             message = text_3.format(gender=az_gender, age_group=az_age_group, interest=az_interest)
#             message += f"\nPremium Statusu: {premium}"
#             if premium:
#                 message += f"\nPremiumun Bitiş Tarixi: {expiry}"
#             message += f"\n\nGöndərilən ümumi mesajlar: {total_msg}\nÜmumi dialoqlar: {dialogs}"
#             message += f"\n\n🔞 Qaydaları pozma sayı: {offense}"
#             edit_button_text = "Redaktə et ✏️"
#             close_button_text = "Bağla ❌"
#         else:
#             return "Invalid language specified."
        
#         # Creating reply markup with two buttons
#         reply_markup = InlineKeyboardMarkup(
#             [
#                [ InlineKeyboardButton(text = edit_button_text, callback_data = "edit_profile"), InlineKeyboardButton(text = close_button_text, callback_data = "close_profile")]
#             ]
#         )
        
#         return message, reply_markup
#     except Exception as e:
#         print("Error in get_profile:", e)
#         return "An error occurred while fetching the profile.", None




















async def get_profile(user_id, language, mode):
    premium, time = is_user_premium(str(user_id))
    user_data = {
        "gender": get_gender(user_id, language),
        "age_group": get_age_group(user_id, language),
        "interest": get_interest(user_id, language),
        "total_msg": users_chat_details(user_id, "total_message"),
        "dialogs": vip_users_details(user_id, "total_dialog"),
        "offense": users_chat_details(user_id, "profanity_score")
    }
    chat_details= users_rating_details(user_id, "rating")
    rating = str(chat_details).replace("{", "").replace("}", "").replace("'", "").replace(",", "")

    if mode == "user_profile":
        message = f"{await translate_async(f"🔎 ID: {user_id}", language)}\n\n🗣 {await translate_async( f"Language:{language}", language)}\n"
        message += f"🗂 {await translate_async('User Data', language)}:\n"
        message += f"👤 {await translate_async('Gender', language)}: {user_data['gender']}\n"
        message += f"🎂 {await translate_async('Age', language)}: {user_data['age_group']}\n"
        message += f"⚡ {await translate_async('Interest', language)}: {user_data['interest']}\n\n"
        message += f"📊 {await translate_async('Rating', language)}: {rating}\n\n"
        message += f"💌 {await translate_async('Invite a friend', language)}: https://t.me/{BOT_USERNAME}?start=r{user_id}\n\n"

        if premium:
            message += f"🌍 {await translate_async('Subscription 💎 PREMIUM: True', language)}\n"
            message += f"🔔 {await translate_async(f'Premium Expiry in: {calculate_remaining_time(time)}', language)}\n"

        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=await translate_async('Edit✍️', language), callback_data="edit_profile")],
                [InlineKeyboardButton(text=await translate_async('Back 🔙', language), callback_data="back_home")]
            ]
        )

    elif mode == "user_statistics":
        # message = f"📅 {await translate_async('Registration', language)}: {user_data['registration']}\n\n"
        message = f"💬 {await translate_async('Dialogues conducted', language)}: {user_data['dialogs']}\n"
        message += f"📩 {await translate_async('Messages sent', language)}: {user_data['total_msg']}\n"
        # message += f"⏳ {await translate_async('Time in dialogues', language)}: {user_data['time_in_dialogues']}s\n\n"
        message += f"🤬 {await translate_async('Swear words sent', language)}: {user_data['offense']}\n"

        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=await translate_async('Back 🔙', language), callback_data="back_home")]
            ]
        )
    
    elif mode == "general":
        message = await translate_async("Choose an option:", language)
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=await translate_async("👁️‍🗨️Profile", language), callback_data="user_profile"
                    ),
                    InlineKeyboardButton(
                        text=await translate_async("🧮Statistics", language), callback_data="user_statistics"
                    ),
                ]
            ]
        )
    else:
            return "Invalid mode specified."

    return message, reply_markup
