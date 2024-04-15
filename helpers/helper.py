from zenova import mongodb as collection
from langdb.profile import text_1, text_2, text_3

key = "aditya"

def add_user_id(language, user_id, field):
    try:
        # Update the stored document
        collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.{language}.{field}": user_id}})
    except Exception as e:
        print("Error in adding user ID:", e)
        
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

def get_gender(user_id):
    try:
        language = find_language(user_id)
        if language:
            stored_data = collection.find_one({key: {"$exists": True}})
            if stored_data and language in stored_data[key]:
                lang_data = stored_data[key][language]
                if "male" in lang_data and user_id in lang_data["male"]:
                    return "male"
                elif "female" in lang_data and user_id in lang_data["female"]:
                    return "female"
    except Exception as e:
        print('Exception occurred in get_gender:', e)
    return None

def get_age_group(user_id):
    language = find_language(user_id)
    age_group_field = find_field(user_id, language, "below_18", "18_24", "25_34", "above_35")
    if age_group_field == "below_18":
        return "Below 18"
    elif age_group_field == "18_24":
        return "18-24"
    elif age_group_field == "25_34":
        return "25-34"
    elif age_group_field == "above_35":
        return "Above 35"
    else:
        return None

def get_interest(user_id):
    language = find_language(user_id)
    interest_field = find_field(user_id, language, "communication", "intimacy", "selling")
    if interest_field:
        return interest_field.capitalize()
    else:
        return None
    
def is_user_registered(user_id):
    print("funcs called:", user_id)
    language = find_language(user_id)
    if language:
        gender = get_gender(user_id)
        age_group = get_age_group(user_id)
        interest = get_interest(user_id)
        print(gender, age_group, interest)
        if gender and age_group and interest:
            return True
        else:
            return False
    else:    
        return False


def get_profile(user_id, language):
    try:
        gender = get_gender(user_id)
        age_group = get_age_group(user_id)
        interest = get_interest(user_id)
        
        if language == "English":
            return text_1.format(gender=gender, age_group=age_group, interest=interest)
        elif language == "Russian":
            return text_2.format(gender=gender, age_group=age_group, interest=interest)
        elif language == "Azerbejani":
            return text_3.format(gender=gender, age_group=age_group, interest=interest)
        else:
            return "Invalid language specified."
    except Exception as e:
        print("Error in get_profile:", e)
        return "An error occurred while fetching the profile."

