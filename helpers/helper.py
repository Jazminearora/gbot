from Modules import mongodb as collection, BOT_USERNAME
from database.referdb import get_point
from config import key
from helpers.translator import translate_async
from datetime import timedelta
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
            for age_group in ["-15", "15_17", "18_24", "25_34", "35+"]:
                if str(user_id) in lang_data.get(age_group, []):
                    return age_group.replace("_", "-").capitalize()
    except Exception as e:
        print('Exception occurred in get_age_group:', e)
    return None

def convert_age_group(age):
    if age < 15:
        return "-15"
    elif 15 <= age <= 17:
        return "15_17"
    elif 18 <= age <= 24:
        return "18_24"
    elif 25 <= age <= 34:
        return "25_34"
    elif age >= 35:
        return "35+"
    else:
        print(age)
        return None
    
def get_interest(user_id, _):
    try:
        document = collection.find_one({key: {"$exists": True}})
        if document:
            lang_data = document[key]["database"]
            interests = []
            for interest in ["communication", "intimacy", "selling", "movies", "anime", "music", "gaming", "memes", "relationships", "tiktok", "flirting", "travel", "study", "food", "fitness"]:
                if str(user_id) in lang_data.get(interest, []):
                    interests.append(interest.capitalize())
            return " ".join(interests) if interests else None
    except Exception as e:
        print('Exception occurred in get_interest:', e)
    return None


##================================================================================================##
##================================================================================================##


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

def get_detailed_user_list(language):
    try:
        detailed_list = {}
        users_list = get_users_list(language)
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
            interests= ["communication", "intimacy", "selling", "movies", "anime", "music", "gaming", "memes", "relationships", "tiktok", "flirting", "travel", "study", "food", "fitness"]
            for interest_type in interests:
                total_users = get_total_users(interest_type)
                detailed_list["Interest"][interest_type] = total_users
            return detailed_list
        else:
            return None
    except Exception as e:
        print(f'Error in getting detailed user list for {language}:', e)
        return None
    
##================================================================================================##
##================================================================================================##


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
    
    
##================================================================================================##
##================================================================================================##


async def get_profile(user_id, language, mode):
    try:
        premium, time = is_user_premium(str(user_id))
        user_data = {
            "gender": get_gender(user_id, language),
            "age_group": get_age_group(user_id, language),
            "age": vip_users_details(user_id, "age"),
            "interest": get_interest(user_id, language),
            "total_msg": users_chat_details(user_id, "total_message"),
            "dialogs": vip_users_details(user_id, "total_dialog"),
            "chat_time": str(timedelta(seconds=vip_users_details(user_id, "chat_time"))),
            "weekly_chat_time": str(timedelta(seconds=vip_users_details(user_id, "weekly_chat_time"))),
            "offense": users_chat_details(user_id, "profanity_score"),
            "verified" : "verified ✅" if vip_users_details(user_id, "verified") else "Unverified ❌",
            "total_refers": await get_point(user_id)
        }
        chat_details= users_rating_details(user_id, "rating")
        rating = str(chat_details).replace("{", "").replace("}", "").replace("'", "").replace(",", "")

        if mode == "user_profile":
            full_text = f"""
🔎 ID: {user_id}

🗣 Language: {language}

**🗂 User Data:**
👤 Gender: {user_data['gender']}
🎊 Age: {user_data['age']}
🎂 Age Group: {user_data['age_group']}
⚡ Interest: {user_data['interest']}
🔰 Status: {user_data['verified']}
"""
            message = await translate_async(full_text, language)
            message += f"\n📊 {await translate_async('Rating', language)}: {rating}\n\n"
            message += f"🎭 {await translate_async('Get anonymous', language)}: https://t.me/{BOT_USERNAME}?start=a{user_id}\n"
            message += f"💌 {await translate_async('Invite a friend', language)}: https://t.me/{BOT_USERNAME}?start=r{user_id}\n\n"

            if premium:
                message += f"{await translate_async(f"""
🌍 Subscription 💎 PREMIUM: Active🟢
🔔 Premium Expiry in: {calculate_remaining_time(time)}
""", language)}\n"
            else:
                message += f"{await translate_async('🌍 Subscription 💎 PREMIUM: Inactive🔴', language)}\n"
            reply_markup = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text=await translate_async('Edit✍️', language), callback_data="edit_profile")],
                    [InlineKeyboardButton(text=await translate_async('Back 🔙', language), callback_data="back_home")]
                ]
            )


        elif mode == "user_statistics":
            # message = f"📅 {await translate_async('Registration', language)}: {user_data['registration']}\n\n"
            full_text = f"""
💬 Dialogues conducted: {user_data['dialogs']}
📩 Messages sent: {user_data['total_msg']}

⏳ Time in dialogues: {user_data['chat_time']}
🕦 Weekly time in dialogues: {user_data['weekly_chat_time']}

🤬 Swear words sent: {user_data['offense']}

💎 Users invited: {user_data['total_refers']}
            """
            message = await translate_async(full_text, language)

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
    except Exception as e:
        print("An error occured while fetching profile:", e)