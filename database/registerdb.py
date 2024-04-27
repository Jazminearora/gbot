from config import key
import pymongo
from Modules import mongodb as collection


def add_user_id(language, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.database.{field}": user_id}})
        print("After Adding:", collection.find_one())
    except Exception as e:
        print("Error in adding user ID:", e)

def store_str_id( user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.database.{field}": str(user_id)}})
    except Exception as e:
        print("Error in storing user ID:", e)

def remove_user_id(language, user_id, field):
    try:
        print("Before removal:", collection.find_one())
        collection.update_one({key: {"$exists": True}}, {"$pull": {f"{key}.database.{field}": user_id}})
    except Exception as e:
        print("Error in removing user ID:", e)

def remove_str_id(user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$pull": {f"{key}.database.{field}": {"$in": [str(user_id), user_id]}}})
        print(collection.find_one())
    except Exception as e:
        print("Error in removing user ID:", e)