from Modules import referdb

async def is_served_user(refered_user_id: int) -> bool:
    try:
        # Check if any user has referred the given user_id
        for document in referdb.find():
            if refered_user_id in document["referred_users"]:
                return True
        return False
    except Exception as e:
        print("Error:", e)
        return False

async def save_id(referer_user_id: int, refered_user_id: int):
    try:
        referer_key = f"r{referer_user_id}"
        # Check if the referring user already exists in the database
        user = referdb.find_one({"user_id": referer_key})
        if user:
            # If user exists, update the referred users list
            if refered_user_id not in user["referred_users"]:
                user["referred_users"].append(refered_user_id)
                user["points"] += 1  # Increment points by 1 for each referral
                referdb.update_one({"user_id": referer_key}, {"$set": {"referred_users": user["referred_users"], "points": user["points"]}})
                print(user = referdb.find_one({"user_id": referer_key}))
        else:
            # If user does not exist, insert a new document with points initialized to 1
            referdb.insert_one({"user_id": referer_key, "referred_users": [refered_user_id], "points": 1})
    except Exception as e:
        print("Error:", e)

async def get_point(user_id: int) -> int:
    try:
        referer_key = f"r{user_id}"
        # Retrieve the user document from the database
        user = referdb.find_one({"user_id": referer_key})
        if user:
            # Return the total points of the user
            return user.get("points", 0)
        else:
            return 0
    except Exception as e:
        print("Error:", e)
        return 0

async def get_top_referers() -> list:
    try:
        # Retrieve all documents from the database
        referers = referdb.find()
        # Create a list to store the top 5 referers
        top_referers = []
        # Iterate over the documents and create a list of tuples (referer_id, points)
        referer_points = [(document["user_id"][1:], document["points"]) for document in referers]
        # Sort the list in descending order based on points
        referer_points.sort(key=lambda x: x[1], reverse=True)
        # Select the top 5 referers
        top_referers = referer_points[:5]
        return top_referers
    except Exception as e:
        print("Error:", e)
        return []