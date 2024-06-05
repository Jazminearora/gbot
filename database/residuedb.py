from Modules import residuedb, ADMIN_IDS
from pyrogram import filters

# Cache to store blocked users
blocked_users_cache = set()

# Function to add a user to the blocklist
async def add_bluser(user_id: int):
    # Check if user is already blocked
    if await is_blocked(user_id):
        return False

    # Check if user is already blocked in the database
    blocked_users = residuedb.find_one({"_id": "BlockedUsers"})
    if blocked_users and user_id in blocked_users["users"]:
        return False

    # Add user to the blocklist in the database
    if not blocked_users:
        residuedb.insert_one({"_id": "BlockedUsers", "users": [user_id]})
    else:
        blocked_users["users"].append(user_id)
        residuedb.update_one({"_id": "BlockedUsers"}, {"$set": {"users": blocked_users["users"]}})

    # Add user to the cache
    blocked_users_cache.add(user_id)

    return True


# Function to unblock a user
async def unblock_user(user_id: int):
    # Remove user from the cache
    blocked_users_cache.discard(user_id)

    # Remove user from the blocklist in the database
    blocked_users = residuedb.find_one({"_id": "BlockedUsers"})
    if blocked_users and user_id in blocked_users["users"]:
        blocked_users["users"].remove(user_id)
        residuedb.update_one({"_id": "BlockedUsers"}, {"$set": {"users": blocked_users["users"]}})


##================================================================================================##
##================================================================================================##


# Function to check if a user is blocked
async def is_blocked(user_id: int):
    # Check if user is in the cache
    if user_id in blocked_users_cache:
        return True

    # Check if user is blocked in the database
    blocked_users = residuedb.find_one({"_id": "BlockedUsers"})
    if blocked_users and user_id in blocked_users["users"]:
        # Add user to the cache
        blocked_users_cache.add(user_id)
        return True
    return False

async def is_blckd(user_id: int):
    # Check if user is in the cache
    if user_id in blocked_users_cache:
        return True

    # Check if user is blocked in the database
    blocked_users = residuedb.find_one({"_id": "BlockedUsers"})
    if blocked_users and user_id in blocked_users["users"]:
        # Add user to the cache
        blocked_users_cache.add(user_id)
        return True
    return False


##================================================================================================##
##================================================================================================##


async def BLfilter(filter, client, update):
    user_id = int(update.from_user.id)
    if user_id in ADMIN_IDS:
        return False
    banned = await is_blocked(user_id)
    if banned:
        return True
    else:
        return False
    
BLuser = filters.create(BLfilter)


##================================================================================================##
##================================================================================================##


async def store_roulette_history(user_id: int, time_string: str):
    # Update the premium history in the database
    residuedb.update_one(
        {"_id": "premium_history", "history.user_id": user_id},
        {"$push": {"history.$.time_strings": {"$each": [time_string], "$slice": -6}}},
        upsert=True
    )

async def get_roulhist(user_id: int):
    # Query the premium history collection
    result = residuedb.find_one({"_id": "premium_history", "history.user_id": user_id})

    # Extract the last 6 time strings from the history array
    if result:
        history = next((h for h in result["history"] if h["user_id"] == user_id), None)
        if history:
            last_6_purchases = history["time_strings"][-6:]
            return last_6_purchases
    return []