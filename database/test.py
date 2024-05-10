from pymongo import MongoClient
client = MongoClient("mongodb+srv://queenxytra:queenxytra@cluster0.ivuxz80.mongodb.net/?retryWrites=true&w=majority")
db = client["cboSot-primer"]
referdb = db["referdb"]
premiumdb = db["premiumb"]

def save_premium_user(user_id: int, premium_status: bool = None, purchase_time: str = None, expiry_time: str = None, gender: str = None, age_groups: list = None, room: str = None, total_dialog: int = 0, chat_time: int = 0, frens: list = None):
    print("save_premium_user", str(user_id))
    try:
        # Check if the user already exists in the premium database
        existing_user = premiumdb.find_one({"_id": str(user_id)})
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
                update_dict["weekly_chat"] = chat_time


            if update_dict:
                premiumdb.update_one(
                    {"_id": str(user_id)},
                    {"$set": update_dict}
                )
        else:
            # If user does not exist, insert a new document
            if premium_status is None:
                new_status = False
            else:
                new_status = premium_status
            doc = {
                "_id": str(user_id),
                "premium_status": new_status,
                "premium_purchase_time": purchase_time,
                "premium_expiry_time": expiry_time,
                "gender": gender,
                "age_groups": age_groups,
                "room": room,
                "total_dialog": total_dialog,
                "chat_time": chat_time,
                "weekly_chat": chat_time, 
                "frens": frens
            }
            premiumdb.insert_one(doc)
    except Exception as e:
        print("Error:", e)

def reset_chatime():
    try:
        result = premiumdb.update_many({}, {"$set": {"chat_time": 0}})
        return result.modified_count
    except Exception as e:
        print("Error:", e)
        return None

# reset_chatime()


# premiumdb.find_one_and_delete({"_id": 140512778568208})
# premiumdb.find_one_and_delete({"_id": 140210233318032})
# # premiumdb.find_one_and_delete({"_id": '432334334'})

# save_premium_user(7067606707, room="movies" )
# # Fetch all documents from the "premiumdb" collection
# all_documents = premiumdb.find_one({"_id": "7067606707"})
# print(all_documents)
# # # h_doc = referdb.find()
# doc = premiumdb.find()
# for doc in doc:
#     print(doc)

print(str(int(34893480)))
