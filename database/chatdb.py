from Modules import chatdb
from pymongo.errors import PyMongoError

def save_user(user_id: int, total_message: int = 0, profanity_score: int = 0, rating: dict = None):
    try:
        chat_dict = {}
        existing_user = chatdb.find_one({"_id": str(user_id)})
        if existing_user:
            update_ops = {"$inc": {}}
            if total_message!= 0:
                update_ops["$inc"]["total_message"] = total_message
            if profanity_score!= 0:
                update_ops["$inc"]["profanity_score"] = profanity_score
            if rating:
                for emoji, count in rating.items():
                    update_ops["$inc"][f"rating.{emoji}"] = count
                if chat_dict:
                    chatdb.update_one(
                        {"_id": user_id},
                        {"$set": chat_dict}
                    )

            if update_ops:
                chatdb.update_one({"_id": str(user_id)}, update_ops)
        else:
            doc = {
                "_id": str(user_id),
                "total_message": total_message,
                "profanity_score": profanity_score,
                "rating": rating or {"👍": 0, "👎": 0,"🤡": 0, "⛔": 0},
            }
            chatdb.insert_one(doc)
    except PyMongoError as e:
        print("Error:", e)


##================================================================================================##
##================================================================================================##


def users_rating_details(user_id: int, field: str):
    try:
        user = chatdb.find_one({"_id": str(user_id)})
        if user and field in user:
            return user.get(field, {})
        else:
            return {}
    except PyMongoError as e:
        print("Error:", e)
        return {}
    
def users_chat_details(user_id: int, field: str):
    try:
        # Retrieve the user document from the premium database
        user = chatdb.find_one({"_id": str(user_id)})
        if user and field in user:
            return user[field]
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None


##================================================================================================##
##================================================================================================##


def reset_ratings(user_id: int):
    try:
        result = chatdb.update_one({"_id": str(user_id)}, {"$set": {"rating": {}}})
    except PyMongoError as e:
        print("Error:", e)

