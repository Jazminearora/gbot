from zenova import mongodb as collection
from langdb.profile import text_1, text_2, text_3
from config import key
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def add_user_id(language, user_id, field):
    try:
        # Update the stored document
        collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.{language}.{field}": user_id}})
        print("success lang:", language)
    except Exception as e:
        print("Error in adding user ID:", e)

def remove_user_id(language, user_id, field):
    try:
        # Remove user ID from the specified field and language
        collection.update_one({key: {"$exists": True}}, {"$pull": {f"{key}.{language}.{field}": user_id}})
    except Exception as e:
        print(f"Error in removing user ID from {field}:", e)

        
def find_language(user_id):
    stored_data = collection.find_one({key: {"$exists": True}})
    if stored_data:
        for language, lang_data in stored_data[key].items():
            for field, user_ids in lang_data.items():
                if user_id in user_ids:
                    return language
    else:
        return None

def find_field(user_id, language, *fields):
    stored_data = collection.find_one({key: {"$exists": True}})
    if stored_data and language in stored_data[key]:
        lang_data = stored_data[key][language]
        for field in fields:
            if field in lang_data and user_id in lang_data[field]:
                return field
    return None

def get_gender(user_id, language):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document and language in document[key]:
            lang_data = document[key][language]
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
        if document and language in document[key]:
            lang_data = document[key][language]
            for age_group in ["below_18", "18_24", "25_34", "above_35"]:
                if str(user_id) in lang_data.get(age_group, []):
                    return age_group.replace("_", " ").capitalize()
    except Exception as e:
        print('Exception occurred in get_age_group:', e)
    return None

def get_interest(user_id, language):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document and language in document[key]:
            lang_data = document[key][language]
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


def edit_language(user_id, old_lang, new_lang):
    try:
        # Extract information from the old language
        gender = get_gender(user_id, old_lang)
        age_group = get_age_group(user_id, old_lang)
        interest = get_interest(user_id, old_lang)

        try:
            # Remove user ID from fields of the old language
            remove_user_id(old_lang, user_id, "users")
            if gender:
                remove_user_id(old_lang, user_id, gender)
            if age_group:
                remove_user_id(old_lang, user_id, age_group.replace(" ", "_").lower())
            if interest:
                remove_user_id(old_lang, user_id, interest.lower())
        except Exception as e:
            print(f"Error caught while removing user id: {e}")

        try:
            # Store user ID in the users field of the new language
            star = add_user_id(new_lang, user_id, "users")
            if star:
                print("success")
        except Exception as e:
            print(f"Error caught while adding user id: {e}")

        try:
            # Update gender, age group, and interest fields in the new language
            if gender:
                add_user_id(new_lang, user_id, gender)
                print ("True")
            if age_group:
                add_user_id(new_lang, user_id, age_group.replace(" ", "_").lower())
            if interest:
                add_user_id(new_lang, user_id, interest.lower())
        except Exception as e:
            print(f"Error caught while adding user id: {e}")
    except Exception as e:
        print("Error in change_language:", e)
        return False