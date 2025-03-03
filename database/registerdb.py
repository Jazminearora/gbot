from config import key
from Modules import mongodb as collection
import logging

from helpers.helper import convert_age_group
from database.premiumdb import save_premium_user


def add_user_id(_, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.database.{field}": user_id}})
    except Exception as e:
        print("Error in adding user ID:", e)

def store_age(user_id, age):
    try:
        if age == "-15" or age == "35+":
            age_group = age
        else:
            age_group = convert_age_group(int(age))
        add_user_id("_", user_id, age_group)
        save_premium_user(user_id, age)
        print("saving age" ,{age_group}, {age})
    except Exception as e:
        print("Error in adding Age:", e)

def store_str_id(user_id, field):
    try:
        # Check if the field exists
        if collection.find_one({key: {"$exists": True}, f"{key}.database.{field}": {"$exists": True}}):
            # If the field exists, update it
            collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.database.{field}": str(user_id)}})
        else:
            # If the field does not exist, create it and log the creation
            logging.info(f"Creating new field {field} in {key}.database")
            collection.update_one({key: {"$exists": True}}, {"$set": {f"{key}.database.{field}": [str(user_id)]}})
    except Exception as e:
        logging.error(f"Error in storing user ID: {e}")


##================================================================================================##
##================================================================================================##


def remove_user_id(_, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$pull": {f"{key}.database.{field}": user_id}})
    except Exception as e:
        print("Error in removing user ID:", e)

def remove_str_id(user_id, field):
    try:
        updt = collection.update_one({key: {"$exists": True}}, {"$pull": {f"{key}.database.{field}": {"$in": [str(user_id), user_id]}}})
    except Exception as e:
        print("Error in removing user ID:", e)