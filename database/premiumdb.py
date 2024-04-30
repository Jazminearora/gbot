from Modules import premiumdb
from config import EXTEND_HRS_REFER
import time
from datetime import datetime, timedelta

async def save_premium_user(user_id: int, premium_status: bool = None, purchase_time: str = None, expiry_time: str = None, gender: str = None, age_groups: list = None, room: str = None, total_dialog: int = 0, chat_time: int = 0, frens: list = None):
    try:
        # Check if the user already exists in the premium database
        existing_user = premiumdb.find_one({"_id": user_id})
        if existing_user:
            # If user exists, update the premium status and other details
            update_dict = {}
            if premium_status is not None:
                update_dict["premium_status"] = premium_status
            if purchase_time is not None:
                update_dict["premium_purchase_time"] = purchase_time
            if expiry_time is not None:
                update_dict["premium_expiry_time"] = expiry_time
            if gender is not None:
                update_dict["gender"] = gender
            if age_groups is not None:
                update_dict["age_groups"] = age_groups
            if room is not None:
                update_dict["room"] = room
            if frens is not None:
                update_dict["frens"] = frens
            if total_dialog != 0:
                update_dict["total_dialog"] = total_dialog
            if chat_time != 0:
                update_dict["chat_time"] = chat_time


            if update_dict:
                premiumdb.update_one(
                    {"_id": user_id},
                    {"$set": update_dict}
                )
        else:
            # If user does not exist, insert a new document
            if premium_status is None:
                new_status = False
            else:
                new_status = premium_status
            doc = {
                "_id": user_id,
                "premium_status": new_status,
                "premium_purchase_time": purchase_time,
                "premium_expiry_time": expiry_time,
                "gender": gender,
                "age_groups": age_groups,
                "room": room,
                "total_dialog": total_dialog,
                "chat_time": chat_time, 
                "frens": frens
            }
            premiumdb.insert_one(doc)
    except Exception as e:
        print("Error:", e)


async def is_user_premium(user_id: int):
    try:
        # Retrieve the user document from the premium database
        user = premiumdb.find_one({"_id": user_id})
        if user:
            premium_status = user.get("premium_status", False)
            expiry_time = user.get("premium_expiry_time", None)
            # If user is premium
            if premium_status:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                # If expiry time is not over
                if expiry_time and expiry_time > current_time:
                    return True, expiry_time
                else:
                    # If expiry time is over, update premium status to False
                    premiumdb.update_one(
                        {"_id": user_id},
                        {"$set": {"premium_status": False}}
                    )
                    return False, None
            else:
                # If user is not premium, return False
                return False, None
        else:
            # If user does not exist, return False
            return False, None
    except Exception as e:
        print("Error:", e)
        return False, None
    

async def vip_users_details(user_id: int, field: str):
    try:
        # Retrieve the user document from the premium database
        user = premiumdb.find_one({"_id": user_id})
        if user and field in user:
            return user[field]
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None
    
async def extend_premium_user(user_id: int):
    try:
        # Check if the user is already premium
        is_premium, expiry_time = await is_user_premium(user_id)
        if is_premium:
            # If user is premium, extend the expiry time by 2 hours
            new_expiry_time = (datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=EXTEND_HRS_REFER)).strftime("%Y-%m-%d %H:%M:%S")
            premiumdb.update_one(
                {"_id": user_id},
                {"$set": {"premium_expiry_time": new_expiry_time}}
            )
            print(f"Premium extended for user {user_id} to {new_expiry_time}.")
        else:
            # If user is not premium, add them as a new premium user
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            expiry_time = (datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
            await save_premium_user(user_id, premium_status=True, purchase_time=current_time, expiry_time=expiry_time)
            print(f"User {user_id} added as premium until {expiry_time}.")
    except Exception as e:
        print("Error:", e)

async def extend_premium_user_hrs(user_id: int, extend_hrs: int):
    try:
        # Check if the user is already premium
        is_premium, expiry_time = await is_user_premium(user_id)
        if is_premium:
            # If user is premium, extend the expiry time by 2 hours
            new_expiry_time = (datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=extend_hrs)).strftime("%Y-%m-%d %H:%M:%S")
            premiumdb.update_one(
                {"_id": user_id},
                {"$set": {"premium_expiry_time": new_expiry_time}}
            )
            print(f"Premium extended for user {user_id} to {new_expiry_time}.")
        else:
            # If user is not premium, add them as a new premium user
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            expiry_time = (datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=extend_hrs)).strftime("%Y-%m-%d %H:%M:%S")
            await save_premium_user(user_id, premium_status=True, purchase_time=current_time, expiry_time=expiry_time)
            print(f"User {user_id} added as premium until {expiry_time}.")
    except Exception as e:
        print("Error:", e)

async def calculate_remaining_time(expiry_time):
    expiry_datetime = datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.utcnow()
    time_difference = expiry_datetime - current_time

    # Format the remaining time using days, seconds, and microseconds
    remaining_time = timedelta(days=time_difference.days, seconds=time_difference.seconds)
    return remaining_time

async def remove_item_from_field(user_id: int, field: str, item: any):
    try:
        # Retrieve the user document from the premium database
        user = premiumdb.find_one({"_id": user_id})
        if user and field in user:
            field_value = user[field]
            if isinstance(field_value, list):
                # If the field value is a list, remove the item from the list
                if item in field_value:
                    field_value.remove(item)
                    premiumdb.update_one(
                        {"_id": user_id},
                        {"$set": {field: field_value}}
                    )
                    print(f"Item {item} removed from field {field} for user {user_id}.")
                else:
                    print(f"Item {item} not found in field {field} for user {user_id}.")
            elif isinstance(field_value, str):
                # If the field value is a string, cannot remove an item from a string
                print(f"Field {field} is a string, cannot remove an item from it for user {user_id}.")
            else:
                # If the field value is neither a list nor a string, raise an error
                raise ValueError(f"Unsupported field type for field {field} for user {user_id}.")
        else:
            print(f"Field {field} not found for user {user_id}.")
    except Exception as e:
        print("Error:", e)


async def get_premium_users():
    try:
        premium_users = premiumdb.find({})
        premium_user_ids = []
        total_premium_users = 0
        for user in premium_users:
            user_id = user["_id"]
            is_premium, _ = await is_user_premium(user_id)
            if is_premium:
                premium_user_ids.append(user_id)
                total_premium_users += 1
        return premium_user_ids, total_premium_users
    except Exception as e:
        print("Error:", e)
        return [], 0


async def get_top_chat_users(user_id: int = None):
    try:
        print(premiumdb.find_one())
        # Get all users sorted by chat_time in descending order
        users = premiumdb.find().sort("chat_time", -1)

        # Get the top 5 users
        top_users = []
        for user in users.limit(5):
            top_users.append({"user_id": user["_id"], "chat_time": user["chat_time"]})

        # If user_id is provided, find the position and chat time of that user
        if user_id:
            user_position = 0
            user_chat_time = 0
            for i, user in enumerate(users):
                if user["_id"] == user_id:
                    user_position = i + 1
                    user_chat_time = user["chat_time"]
                    break
            return top_users, user_position, user_chat_time
        else:
            return top_users
    except Exception as e:
        print("Error:", e)
        return []