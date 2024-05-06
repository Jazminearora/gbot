from pymongo import MongoClient
from bson.son import SON
import pymongo

client = MongoClient("mongodb+srv://MRDAXX:MRDAXX@mrdaxx.prky3aj.mongodb.net/?retryWrites=true&w=majority")
db = client["cboSot-primer"]
chatdb = db["chatdb"]

def save_user(user_id: int, total_chat: int = 0, total_message: int = 0, total_dialogues: int = 0, profanity_score: int = 0, rating: dict = None, chat_time: int = 0, frens: list = None):
    try:
        existing_user = chatdb.find_one({"_id": user_id})
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
                    update_ops["$inc"][f"rating.{emoji}"] = count
            if chat_time!= 0:
                update_ops["$inc"]["chat_time"] = chat_time
            if frens:
                update_ops["$addToSet"]["frens"] = {"$each": frens}

            if update_ops:
                chatdb.update_one({"_id": user_id}, update_ops)
        else:
            doc = {
                "_id": user_id,
                "total_chat": total_chat,
                "total_message": total_message,
                "total_dialogues": total_dialogues,
                "profanity_score": profanity_score,
                "rating": rating or {},
                "chat_time": chat_time,
                "frens": frens or []
            }
            chatdb.insert_one(doc)
    except pymongo.errors.PyMongoError as e:
        print("Error:", e)


def users_chat_details(user_id: int, field: str):
    try:
        user = chatdb.find_one({"_id": user_id})
        if user and field in user:
            return user.get(field, {})
        else:
            return {}
    except pymongo.errors.PyMongoError as e:
        print("Error:", e)
        return {}

save_user(1567526737, rating={"😐": 1})
chat_details = users_chat_details(1567526737, "rating")
result = str(chat_details).replace("{", "").replace("}", "").replace("'", "").replace(",", "")
print(result)


# def reset_ratings(user_id: int):
#     try:
#         chatdb.update_one({"_id": user_id}, {"$set": {"rating": {}}})
#     except pymongo.errors.PyMongoError as e:
#         print("Error:", e)
# 💩
# reset_ratings(5131723020)
