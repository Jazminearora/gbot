from config import key
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
        document = collection.find_one({key: {"$exists": True}})
        if document:
            lang_data = document[key]["database"]
            for interest in ["communication", "intimacy", "selling"]:
                if str(user_id) in lang_data.get(interest, []):
                    # Remove the user ID from the interest list
                    lang_data[interest].remove(str(user_id))
                    # Update the document in the database
                    collection.update_one({"_id": document["_id"]}, {"$set": {key: {"database": lang_data}}})
                    return f"User ID {user_id} removed from {interest.capitalize()}."
    except Exception as e:
        print('Exception occurred in remove_interest:', e)
    return None