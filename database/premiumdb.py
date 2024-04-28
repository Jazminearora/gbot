from Modules import premiumdb
from config import EXTEND_HRS_REFER
import time
from datetime import datetime, timedelta

async def save_premium_user(user_id: int, premium_status: bool = None, purchase_time: str = None, expiry_time: str = None, gender: str = None, age_groups: list = None, room: str = None):
    try:
        print(premium_status)
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
                "room": room
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