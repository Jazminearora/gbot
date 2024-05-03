from Modules import chatdb

def save_user(user_id: int, total_chat: int = 0, total_message: int = 0, total_dialogues: int = 0, profanity_score: int = 0, rating: dict = None, chat_time: int = 0, frens: list = None):
    try:
        # Check if the user already exists in the users database
        existing_user = chatdb.find_one({"_id": user_id})
        if existing_user:
            # If user exists, update the user details
            update_dict = {}
            if total_chat != 0:
                update_dict["$inc"] = {"total_chat": total_chat}
            if total_message != 0:
                update_dict["$inc"]["total_message"] = total_message
            if total_dialogues != 0:
                update_dict["$inc"]["total_dialogues"] = total_dialogues
            if profanity_score != 0:
                update_dict["$inc"]["profanity_score"] = profanity_score
            if rating is not None:
                for emoji, count in rating.items():
                    update_dict["$inc"][f"rating.{emoji}"] = count
            if chat_time != 0:
                update_dict["$inc"]["chat_time"] = chat_time
            if frens is not None:
                update_dict["$addToSet"]["frens"] = frens

            if update_dict:
                chatdb.update_one(
                    {"_id": user_id},
                    update_dict
                )
        else:
            # If user does not exist, insert a new document
            doc = {
                "_id": user_id,
                "total_chat": total_chat,
                "total_message": total_message,
                "total_dialogues": total_dialogues,
                "profanity_score": profanity_score,
                "rating": rating if rating is not None else {},
                "chat_time": chat_time,
                "frens": frens if frens is not None else []
            }
            chatdb.insert_one(doc)
    except Exception as e:
        print("Error:", e)


def users_chat_details(user_id: int, field: str):
    try:
        # Retrieve the user document from the premium database
        user = chatdb.find_one({"_id": user_id})
        if user and field in user:
            return user[field]
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None