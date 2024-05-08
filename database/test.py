list = [
  {
    "_id": 5131723020,
    "premium_status": False,
    "premium_purchase_time": None,
    "premium_expiry_time": None,
    "gender": "female",
    "age_groups": ["Below-18"],
    "room": "any",
    "total_dialog": 20,
    "chat_time": 357,
    "frens": None
  },
  {
    "_id": 1567526737,
    "premium_status": False,
    "premium_purchase_time": None,
    "premium_expiry_time": None,
    "gender": None,
    "age_groups": None,
    "room": None,
    "total_dialog": 19,
    "chat_time": 114,
    "frens": None
  },
  {
    "_id": 7067606707,
    "premium_status": False,
    "premium_purchase_time": None,
    "premium_expiry_time": None,
    "gender": None,
    "age_groups": None,
    "room": None,
    "total_dialog": 1,
    "chat_time": 36,
    "frens": None
  }
]


def get_user_position(users_list, user_id: int):
    try:
        for index, user in enumerate(users_list):
            if user["_id"] == user_id:
                return index + 1  # Position starts from 1
        return None  # User ID not found in the list
    except Exception as e:
        print("Error:", e)
        return None

# Yahaan 'users_list' aapki di gayi list hai aur 'user_id' user ki ID hai jiski position nikalni hai
user_id = 5131723020  # Example user ID
position = get_user_position(list, user_id)
if position is not None:
    print(f"User {user_id} ki position chat time ke adhaar pe: {position}")
else:
    print("User ID list mein nahi hai.")
