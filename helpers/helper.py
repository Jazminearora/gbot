from zenova import mongodb as collection
from langdb.profile import text_1, text_2, text_3
from config import key
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def add_user_id(language, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.database.{field}": user_id}})
        print("success lang:", language)
    except Exception as e:
        print("Error in adding user ID:", e)

def remove_user_id(language, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$pull": {f"{key}.database.{field}": user_id}})
        print("success removal:", language)
    except Exception as e:
        print("Error in removing user ID:", e)

def find_language(user_id):
    stored_data = collection.find_one({key: {"$exists": True}})
    print("stored_data:", stored_data)
    if stored_data:
        for language, lang_data in stored_data[key]["database"].items():
            if language in ["English", "Russian", "Azerbejani"] and user_id in lang_data:
                return language
    return None

def get_total_users(language):
    try:
        total_users = 0
        document = collection.find_one({key: {"$exists": True}})
        if document and language in document[key]["database"]:
            lang_data = document[key]["database"][language]
            if "users" in lang_data:
                total_users += len(lang_data["users"])
        return total_users
    except Exception as e:
        print(f'Error in getting total users for {language}:', e)
        return None

def get_gender(user_id, language):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document:
            database = document[key].get("database", {})
            for lang_data in database.values():
                if user_id in lang_data.get("male", []):
                    return "male"
                elif user_id in lang_data.get("female", []):
                    return "female"
    except Exception as e:
        print('Error in getting gender:', e)
    return None


def get_age_group(user_id, language):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document and language in document[key]["database"]:
            lang_data = document[key]["database"][language]
            for age_group in ["below_18", "18_24", "25_34", "above_35"]:
                if str(user_id) in lang_data.get(age_group, []):
                    return age_group.replace("_", "-").capitalize()
    except Exception as e:
        print('Exception occurred in get_age_group:', e)
    return None

def get_interest(user_id, language):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document and language in document[key]["database"]:
            lang_data = document[key]["database"][language]
            for interest in ["communication", "intimacy", "selling"]:
                if str(user_id) in lang_data.get(interest, []):
                    return interest.capitalize()
    except Exception as e:
        print('Exception occurred in get_interest:', e)
    return None
    
def is_user_registered(user_id):
    print("funcs called:", user_id)
    language = find_language(user_id)
    print("language:", language)
    if language:
        gender = get_gender(user_id, language)
        age_group = get_age_group(user_id, language)
        interest = get_interest(user_id, language)
        print(gender, age_group, interest)
        if gender and age_group and interest:
            return True
        else:
            return False
    else:    
        return False


def get_profile(user_id, language):
    try:
        gender = get_gender(user_id, language)
        age_group = get_age_group(user_id, language)
        interest = get_interest(user_id, language)
        
        if language == "English":
            message = text_1.format(gender=gender, age_group=age_group, interest=interest)
            edit_button_text = "Edit ✏️"
            close_button_text = "Close ❌"
        elif language == "Russian":
            message = text_2.format(gender=gender, age_group=age_group, interest=interest)
            edit_button_text = "Редактировать ✏️"
            close_button_text = "Закрыть ❌"
        elif language == "Azerbejani":
            message = text_3.format(gender=gender, age_group=age_group, interest=interest)
            edit_button_text = "Redaktə et ✏️"
            close_button_text = "Bağla ❌"
        else:
            return "Invalid language specified."
        
        # Creating reply markup with two buttons
        reply_markup = InlineKeyboardMarkup(
            [
               [ InlineKeyboardButton(text = edit_button_text, callback_data = "edit_profile"), InlineKeyboardButton(text = close_button_text, callback_data = "close_profile")]
            ]
        )
        
        return message, reply_markup
    except Exception as e:
        print("Error in get_profile:", e)
        return "An error occurred while fetching the profile.", None


