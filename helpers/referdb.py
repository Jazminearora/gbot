from zenova import referdb

async def is_served_user(refered_user_id: int) -> bool:
    for document in referdb.find():
        for key, value in document.items():
            if isinstance(value, list) and refered_user_id in value:
                return True
    return False

async def save_id(referer_user_id: int, refered_user_id: int):
    try:
        referer_key = f"r{referer_user_id}"
        user = await referdb.find_one({referer_key: {"$exists": True}})
        if user:
            referer_ids = user.get(referer_key, [])
            if refered_user_id not in referer_ids:
                referer_ids.append(refered_user_id)
                await referdb.update_one({referer_key: {"$exists": True}}, {"$set": {referer_key: referer_ids}})
                return True
            else:
                return True
        else:
            await referdb.insert_one({referer_key: [refered_user_id]})
            return True
    except:
        return False

async def referral_count(user_id: int) -> int:
    try:
        referer_key = f"r{user_id}"
        user = await referdb.find_one({referer_key: {"$exists": True}})
        if user:
            referer_ids = user.get(referer_key, [])
            return referer_ids
        else:
            return []
    except Exception as e:
        print("Error:", e)
        return []