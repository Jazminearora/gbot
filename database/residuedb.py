from Modules import residuedb, ADMIN_IDS
from pyrogram import filters
# Cache to store blocked users
blocked_users_cache = set()

# Function to add a user to the blocklist
async def add_bluser(user_id):
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
async def unblock_user(user_id):
    # Remove user from the cache
    blocked_users_cache.discard(user_id)

    # Remove user from the blocklist in the database
    blocked_users = residuedb.find_one({"_id": "BlockedUsers"})
    if blocked_users and user_id in blocked_users["users"]:
        blocked_users["users"].remove(user_id)
        residuedb.update_one({"_id": "BlockedUsers"}, {"$set": {"users": blocked_users["users"]}})


# Function to check if a user is blocked
async def is_blocked(user_id):
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


async def BLfilter(filter, client, update):
    user_id = update.from_user.id
    if user_id in ADMIN_IDS:
        return False
    banned = is_blocked(user_id)
    if banned:
        return True
    else:
        return False
    
BLuser = filters.create(BLfilter)
