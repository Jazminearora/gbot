from config import key
import pymongo
from Modules import mongodb as collection


def add_user_id(language, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$push": {f"{key}.database.{field}": user_id}})
    except Exception as e:
        print("Error in adding user ID:", e)

def remove_user_id(language, user_id, field):
    try:
        collection.update_one({key: {"$exists": True}}, {"$pull": {f"{key}.database.{field}": user_id}})
    except Exception as e:
        print("Error in removing user ID:", e)

def remove_interest(user_id):
    try:
        # Assuming 'collection' is a MongoDB collection object
        # and 'key' is the field name where the interests are stored
        filter = {key: {"$exists": True}}
        update = {"$pull": {}}
        for interest in ["communication", "intimacy", "selling", "movies", "anime"]:
            print (interest)
            update["$pull"][f"{key}.database.{interest}"] = str(user_id)
        
        result = collection.find_one_and_update(filter, update, return_document=pymongo.ReturnDocument.AFTER)
        
        if result:
            return f"User ID {user_id} removed from interests."
        else:
            return f"User ID {user_id} not found in interests."
    except Exception as e:
        print('Exception occurred in remove_interest:', e)
    return None