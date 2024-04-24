from zenova import mongodb as collection
from langdb.profile import text_1, text_2, text_3
from config import key
from helpers.translator import translate_text
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import filters

def add_user_id(language, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.database.{field}": user_id}})
    except Exception as e:
        print("Error in adding user ID:", e)

def remove_user_id(language, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$pull": {f"{key}.database.{field}": user_id}})
    except Exception as e:
        print("Error in removing user ID:", e)

def remove_interest(user_id):
    try:
        # Assuming 'collection' is a MongoDB collection object
        # and 'key' is the field name where the interests are stored
        document = collection.find_one({key: {"$exists": True}})
        if document:
            lang_data = document[key]["database"]
            for interest in ["communication", "intimacy", "selling"]:
                if str(user_id) in lang_data.get(interest, []):
                    # Remove the user ID from the interest list
                    lang_data[interest].remove(str(user_id))
                    # Update the document in the database
                    collection.update_one({"_id": document["_id"]}, {"$set": {key: {"database": lang_data}}})
                    return f"User ID {user_id} removed from {interest.capitalize()}."
    except Exception as e:
        print('Exception occurred in remove_interest:', e)
    return None


def find_language(user_id):
    stored_data = collection.find_one({key: {"$exists": True}})
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
            total_users += len(lang_data)  # lang_data is a list, so use len directly
        return total_users
    except Exception as e:
        print(f'Error in getting total users for {language}:', e)
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

def get_interest(user_id, language):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document:
            lang_data = document[key]["database"]
            for interest in ["communication", "intimacy", "selling"]:
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
            ru_gender = translate_text(gender, target_language="ru")
            ru_age_group = translate_text(age_group, target_language="ru")
            ru_interest = translate_text(interest, target_language="ru")
            message = text_2.format(gender=ru_gender, age_group=ru_age_group, interest=ru_interest)
            edit_button_text = "Редактировать ✏️"
            close_button_text = "Закрыть ❌"
        elif language == "Azerbejani":
            az_gender = translate_text(gender, target_language="az")
            az_age_group = translate_text(age_group, target_language="az")
            az_interest = translate_text(interest, target_language="az")
            message = text_3.format(gender=az_gender, age_group=az_age_group, interest=az_interest)
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


