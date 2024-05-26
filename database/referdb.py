from Modules import referdb, logging
from random import randint

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
    
async def create_refer_program(
    id: int = None, 
    admin_ids: list = None, 
    promotion_name: str = None, 
    referred_users: list = None, 
    points: int = 0
) -> int:
    """
    Create a new referral program or update an existing one.
    
    Args:
        id (int): The ID of the referral program (optional).
        admin_ids (list): The IDs of the administrators.
        promotion_name (str): The name of the promotion.
        referred_users (list): The list of referred users.
        points (int): The points awarded for each referral.
    
    Returns:
        int: The ID of the created or updated referral program.
    """
    if id is None:
        id = randint(111111, 999999) # do not edit this

    refer_program = {
        '_id': id, 
        'admins_id': admin_ids, 
        'name': promotion_name, 
        'referred_users': referred_users or [], 
        'points': points
    }

    existing_program = referdb.find_one({'_id': id}) if referdb.find_one({'_id': id}) else referdb.find_one({'name': promotion_name}) 
    if existing_program:
        if referred_users:
            existing_program['referred_users'].append(referred_users)
            existing_program['points'] += points
            referdb.update_one({'_id': id}, {'$set': {'referred_users': existing_program['referred_users'], 'points': existing_program['points']}})
        return id
    else:
        referdb.insert_one({'is_active': True, **refer_program})
        return id

async def get_refer_programs_data():
    programs = referdb.find({'is_active': True})
    return [{'id': program['_id'], 'name': program['name'], 'admins_id': program['admins_id'], 'points': program['points']} for program in programs]

async def delete_refer_program(program_id: int):
    referdb.update_one({'_id': program_id}, {'$set': {'is_active': False}})

async def get_refer_program_field(program_id: int, field: str) -> any:
    try:
        # Retrieve the program document from the database
        program = referdb.find_one({"_id": int(program_id)})
        if program and field in program:
            return program[field]
        else:
            return None
    except Exception as e:
        logging.error("Error: %s", e)
        return None
    
async def is_program_id(id: int) -> tuple:
    program = referdb.find_one({'_id': int(id), 'is_active': True})
    if program:
        return True, program['admins_id']
    return False, []