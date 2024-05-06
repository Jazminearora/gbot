from Modules import chatdb
from pymongo.errors import PyMongoError

async def save_user(user_id: int, total_chat: int = 0, total_message: int = 0, total_dialogues: int = 0, profanity_score: int = 0, rating: dict = None, chat_time: int = 0, frens: list = None):
    print("save user called", user_id, ":", rating)
    try:
        existing_user = chatdb.find_one({"_id": int(user_id)})
        print("existing user:", existing_user)
        if existing_user:
            update_ops = {"$inc": {}}
            if total_chat!= 0:
                update_ops["$inc"]["total_chat"] = total_chat
            if total_message!= 0:
                update_ops["$inc"]["total_message"] = total_message
            if total_dialogues!= 0:
                update_ops["$inc"]["total_dialogues"] = total_dialogues
            if profanity_score!= 0:
                update_ops["$inc"]["profanity_score"] = profanity_score
            if rating:
                for emoji, count in rating.items():
                    print("rating key:", emoji, "count:", count)
                    update_ops["$inc"]["rating"] = {emoji: count} 
            if chat_time!= 0:
                update_ops["$inc"]["chat_time"] = chat_time
            if frens:
                update_ops["$addToSet"]["frens"] = {"$each": frens}

            print("update ops:", update_ops)
            if update_ops:
                result = chatdb.update_one({"_id": user_id}, update_ops)
                print("update result:", result.modified_count)
        else:
            doc = {
                "_id": int(user_id),
                "total_chat": total_chat,
                "total_message": total_message,
                "total_dialogues": total_dialogues,
                "profanity_score": profanity_score,
                "rating": rating or {},
                "chat_time": chat_time,
                "frens": frens or []
            }
            print("inserting doc:", doc)
            chatdb.insert_one(doc)
    except PyMongoError as e:
        print("Error:", e)


def users_chat_details(user_id: int, field: str):
    try:
        user = chatdb.find_one({"_id": int(user_id)})
        print("user:", user)
        if user and field in user:
            return user.get(field, {})
        else:
            return {}
    except PyMongoError as e:
        print("Error:", e)
        return {}
    
def reset_ratings(user_id: int):
    try:
        result = chatdb.update_one({"_id": user_id}, {"$set": {"rating": {}}})
        print("reset ratings result:", result.modified_count)
    except PyMongoError as e:
        print("Error:", e)