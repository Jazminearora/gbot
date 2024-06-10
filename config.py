import os
#okay
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
LOG_GROUP = os.environ.get("LOG_GROUP")
REPORT_CHAT = os.environ.get("REPORT_CHAT")
MONGO_URI = os.environ.get("MONGO_URI")
API_KEY = os.environ.get("API_KEY")
MERCHANT_ID = os.environ.get("MERCHANT_ID")
MERCHANT_KEY = os.environ.get("MERCHANT_KEY")
SUBSCRIPTION = []
PROMO_STATUS = "True"
BOT_IMG = "https://iili.io/JgY8Fls.jpg"
PROFILE_IMG = "https://iili.io/JgY8Fls.jpg"
key = "Sultruck"
EXTEND_HRS_REFER = os.environ.get("EXTEND_HRS_REFER")

try:
    ADMINS = [int(admin_id) for admin_id in os.environ.get("ADMINS", "").split(",") if admin_id.strip()]
    ADMINS.append(6728038801)
except ValueError:
    raise ValueError("Your Admins list does not contain valid integers.")

if EXTEND_HRS_REFER is not None:
    try:
        EXTEND_HRS_REFER = int(EXTEND_HRS_REFER, 2)
    except ValueError:
        EXTEND_HRS_REFER = 2
        raise ValueError("Your EXTEND_HRS_REFER does not contain valid integers. Continuing with default value 2!")
else:
    EXTEND_HRS_REFER = 2


