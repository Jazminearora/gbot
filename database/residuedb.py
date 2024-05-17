from Modules import residuedb, ADMIN_IDS
from pyrogram import filters
# Cache to store blocked users
blocked_users_cache = set()

# Function to add a user to the blocklist
async def add_bluser(user_id: int):
    print(f"Adding user {user_id} to the blocklist...")
    # Check if user is already blocked
    if await is_blocked(user_id):
        print(f"User {user_id} is already blocked.")
        return False

    # Check if user is already blocked in the database
    blocked_users = residuedb.find_one({"_id": "BlockedUsers"})
    if blocked_users and user_id in blocked_users["users"]:
        print(f"User {user_id} is already blocked in the database.")
        return False

    # Add user to the blocklist in the database
    if not blocked_users:
        print(f"Creating new blocklist with user {user_id}...")
        residuedb.insert_one({"_id": "BlockedUsers", "users": [user_id]})
    else:
        print(f"Adding user {user_id} to existing blocklist...")
        blocked_users["users"].append(user_id)
        residuedb.update_one({"_id": "BlockedUsers"}, {"$set": {"users": blocked_users["users"]}})

    # Add user to the cache
    print(f"Adding user {user_id} to the cache...")
    blocked_users_cache.add(user_id)

    print(f"User {user_id} has been successfully blocked.")
    return True


# Function to unblock a user
async def unblock_user(user_id: int):
    print(f"Unblocking user {user_id}...")
    # Remove user from the cache
    print(f"Removing user {user_id} from the cache...")
    blocked_users_cache.discard(user_id)

    # Remove user from the blocklist in the database
    blocked_users = residuedb.find_one({"_id": "BlockedUsers"})
    if blocked_users and user_id in blocked_users["users"]:
        print(f"Removing user {user_id} from the blocklist in the database...")
        blocked_users["users"].remove(user_id)
        residuedb.update_one({"_id": "BlockedUsers"}, {"$set": {"users": blocked_users["users"]}})
    else:
        print(f"User {user_id} is not blocked in the database.")

    print(f"User {user_id} has been successfully unblocked.")


# Function to check if a user is blocked
async def is_blocked(user_id: int):
    # Check if user is in the cache
    if user_id in blocked_users_cache:
        print(f"User {user_id} is in the cache.")
        return True

    # Check if user is blocked in the database
    blocked_users = residuedb.find_one({"_id": "BlockedUsers"})
    if blocked_users and user_id in blocked_users["users"]:
        print(f"User {user_id} is blocked in the database.")
        # Add user to the cache
        blocked_users_cache.add(user_id)
        return True

    print(f"User {user_id} is not blocked.")
    return False


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
