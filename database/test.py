from pymongo import MongoClient
client = MongoClient("mongodb+srv://queenxytra:queenxytra@cluster0.ivuxz80.mongodb.net/?retryWrites=true&w=majority")
db = client["cboSot-primer"]
referdb = db["referdb"]
premiumdb = db["premiumb"]
chatdb = db["chatdsd"]
msg_collection = db["msg_collection"]


# # # def save_premium_user(user_id: int, premium_status: bool = None, purchase_time: str = None, expiry_time: str = None, gender: str = None, age_groups: list = None, room: str = None, total_dialog: int = 0, chat_time: int = 0, frens: list = None):
# # #     print("save_premium_user", str(user_id))
# # #     try:
# # #         # Check if the user already exists in the premium database
# # #         existing_user = premiumdb.find_one({"_id": str(user_id)})
# # #         if existing_user:
# # #             # If user exists, update the premium status and other details
# # #             update_dict = {}
# # #             if premium_status is not None:
# # #                 update_dict["premium_status"] = premium_status
# # #             if purchase_time is not None:
# # #                 update_dict["premium_purchase_time"] = purchase_time
# # #             if expiry_time is not None:
# # #                 update_dict["premium_expiry_time"] = expiry_time
# # #             if gender is not None:
# # #                 update_dict["gender"] = gender
# # #             if age_groups is not None:
# # #                 update_dict["age_groups"] = age_groups
# # #             if room is not None:
# # #                 update_dict["room"] = room
# # #             if frens is not None:
# # #                 update_dict["frens"] = frens
# # #             if total_dialog != 0:
# # #                 update_dict["total_dialog"] = total_dialog
# # #             if chat_time != 0:
# # #                 update_dict["chat_time"] = chat_time
# # #                 update_dict["weekly_chat"] = chat_time


# # #             if update_dict:
# # #                 premiumdb.update_one(
# # #                     {"_id": str(user_id)},
# # #                     {"$set": update_dict}
# # #                 )
# # #         else:
# # #             # If user does not exist, insert a new document
# # #             if premium_status is None:
# # #                 new_status = False
# # #             else:
# # #                 new_status = premium_status
# # #             doc = {
# # #                 "_id": str(user_id),
# # #                 "premium_status": new_status,
# # #                 "premium_purchase_time": purchase_time,
# # #                 "premium_expiry_time": expiry_time,
# # #                 "gender": gender,
# # #                 "age_groups": age_groups,
# # #                 "room": room,
# # #                 "total_dialog": total_dialog,
# # #                 "chat_time": chat_time,
# # #                 "weekly_chat": chat_time, 
# # #                 "frens": frens
# # #             }
# # #             premiumdb.insert_one(doc)
# # #     except Exception as e:
# # #         print("Error:", e)

# # # def reset_chatime():
# # #     try:
# # #         result = premiumdb.update_many({}, {"$set": {"chat_time": 0}})
# # #         return result.modified_count
# # #     except Exception as e:
# # #         print("Error:", e)
# # #         return None

# # # # reset_chatime()


# # # # premiumdb.find_one_and_delete({"_id": 140512778568208})
# # # # premiumdb.find_one_and_delete({"_id": 140210233318032})
# # # # # premiumdb.find_one_and_delete({"_id": '432334334'})

# # # # save_premium_user(7067606707, room="movies" )
# # # # # Fetch all documents from the "premiumdb" collection
# # # # all_documents = premiumdb.find_one({"_id": "7067606707"})
# # # # print(all_documents)
# # # # # # h_doc = referdb.find()
# # # # doc = premiumdb.find()
# # # # for doc in doc:
# # #     # print(doc)
# # # # 
# # # # print(str(int(34893480)))


# # # def save_user(user_id: int, total_message: int = 0, profanity_score: int = 0, rating: dict = None):
# # #     try:
# # #         chat_dict = {}
# # #         existing_user = chatdb.find_one({"_id": str(user_id)})
# # #         if existing_user:
# # #             update_ops = {"$inc": {}}
# # #             if total_message!= 0:
# # #                 update_ops["$inc"]["total_message"] = total_message
# # #             if profanity_score!= 0:
# # #                 update_ops["$inc"]["profanity_score"] = profanity_score
# # #             if rating:
# # #                 for emoji, count in rating.items():
# # #                     update_ops["$inc"][f"rating.{emoji}"] = count
# # #                 if chat_dict:
# # #                     chatdb.update_one(
# # #                         {"_id": user_id},
# # #                         {"$set": chat_dict}
# # #                     )

# # #             if update_ops:
# # #                 chatdb.update_one({"_id": str(user_id)}, update_ops)
# # #         else:
# # #             doc = {
# # #                 "_id": str(user_id),
# # #                 "total_message": total_message,
# # #                 "profanity_score": profanity_score,
# # #                 "rating": rating or {"👍": 0, "👎": 0, "⛔": 0},
# # #             }
# # #             chatdb.insert_one(doc)
# # #     except Exception as e:
# # #         print("Error:", e)

# # # # save_user(3433343, total_message= 1)

# # # def users_chat_details(user_id: int, field: str):
# # #     try:
# # #         # Retrieve the user document from the premium database
# # #         user = chatdb.find_one({"_id": user_id})
# # #         if user and field in user:
# # #             return user[field]
# # #         else:
# # #             return None
# # #     except Exception as e:
# # #         print("Error:", e)
# # #         return None
# # # users_chat_details(str(3433343),"total_message" )
# # # print(users_chat_details(str(3433343),"total_message" ))
# # # # doc = chatdb.find()
# # # # for doc in doc:
# # # #     print(doc)


# from random import randint

# def create_refer_program(
#     id: int = None, 
#     admin_ids: list = None, 
#     promotion_name: str = None, 
#     referred_users: list = None, 
#     points: int = 0
# ) -> int:
#     """
#     Create a new referral program or update an existing one.
    
#     Args:
#         id (int): The ID of the referral program (optional).
#         admin_ids (list): The IDs of the administrators.
#         promotion_name (str): The name of the promotion.
#         referred_users (list): The list of referred users.
#         points (int): The points awarded for each referral.
    
#     Returns:
#         int: The ID of the created or updated referral program.
#     """
#     if id is None:
#         id = randint(111111, 999999)
#         print(id)

#     refer_program = {
#         '_id': id, 
#         'admins_id': admin_ids, 
#         'name': promotion_name, 
#         'referred_users': referred_users or [], 
#         'points': points
#     }

#     existing_program = referdb.find_one({'_id': id})
#     if existing_program:
#         if referred_users:
#             existing_program['referred_users'].append(referred_users)
#             existing_program['points'] += points
#             referdb.update_one({'_id': id}, {'$set': {'referred_users': existing_program['referred_users'], 'points': existing_program['points']}})
#         return id
#     else:
#         referdb.insert_one({'is_active': True, **refer_program})
#         return id
# def get_refer_programs_data():
#     programs = referdb.find({'is_active': True})
#     return [{'id': program['_id'], 'name': program['name'], 'admins_id': program['admins_id'], 'points': program['points']} for program in programs]

# def delete_refer_program(program_id: int):
#     referdb.update_one({'_id': program_id}, {'$set': {'is_active': False}})

# print(get_refer_programs_data())

# create_refer_program(id=400415, promotion_name= "bhoolA", referred_users= 9099090, points= 1)

# create_refer_program(id = 400415, admin_ids=[4390234, 43344233, -1003434324], promotion_name= "shull") #, referred_users= 47394738, points= 1)

# msg_collection.delete_many({'key': 'english'})

# msg_collection.find_one_and_delete({"663f8ab40092d6a76b7fd1bf"})
referdb.delete_one({'_id': 314886})

doc = referdb.find()#{'is_active': True})
for doc in doc:
    print(doc)

def is_served_user(refered_user_id: int) -> bool:
    try:
        # Check if any user has referred the given user_id
        for document in referdb.find():
            if refered_user_id in document["referred_users"]:
                return True
        return False
    except Exception as e:
        print("Error:", e)
        return False
# print(is_served_user(47394738))

