from pymongo import MongoClient

client = MongoClient("")


def get_user_position(users_list, user_id: int) -> tuple:
    """
    Returns the position and chat time of a user in the list.
    """
    print(users_list)
    for index, user in enumerate(users_list):
        if user["_id"] == user_id:
            print("position:", index +1)
            return index + 1, user["chat_time"]  # Position starts from 1
    return None, None  # User ID not found in the list

def get_top_chat_users(user_id: int = None) -> tuple:
    """
    Returns the top 5 chat users and the position of the given user_id.
    """
    try:
        all_users = list(premiumdb.find({"chat_time": {"$gt": 0}}).sort("chat_time", -1))
        top_users = all_users[:5]
        top_users_list = [{"user_id": user["_id"], "chat_time": user["chat_time"]} for user in top_users]

        if user_id:
            user_position, user_chat_time = get_user_position(all_users, user_id)
            return top_users_list, user_position, user_chat_time
        else:
            return top_users_list
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}