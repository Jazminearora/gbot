import os
#okay
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME")
OWNER_ID = int(os.environ.get("OWNER_ID"))
LOGGER_ID = int(os.environ.get("LOGGER_ID"))
MONGO_URI = os.environ.get("MONGO_URI")

try:
    ADMINS=[]
    for x in (os.environ.get("ADMINS", "").split()):
        ADMINS.append(int(x))
except ValueError:
        raise Exception("Your Admins list does not contain valid integers.")
key = "fulala"
DEV_USER = []
SUDO_USERS = os.environ.get("SUDO_USERS")
EXTEND_HRS_REFER = os.environ.get("EXTEND_HRS_REFER")
if EXTEND_HRS_REFER is not None and isinstance(EXTEND_HRS_REFER, str):
    EXTEND_HRS_REFER = int(EXTEND_HRS_REFER, 2)
else:
    EXTEND_HRS_REFER = 2
CHANNEL_USERNAME = '@Equinoxlogs'
SUPPORTING = '@Equinox_Chats'
UPDATE = "https://t.me/EquinoxNetwork"
SUPPORT = "https://t.me/Equinox_Chats"
Bot_join_url = "https://t.me/zenova_VoteBot?startgroup=true"
ERROR_IMG = "https://i.postimg.cc/wTz2NP1N/5ff8d046-d31b-476e-81d2-6b81a231491b.jpg"
Start_img = "https://graph.org/file/d883008fbbafc1609cdc5.jpg"
approved_users = [5265109324, 6790062374]
TUTORIAL_LINK = "https://t.me/Equinox_Chats/492033"

FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {first}\n\n<b>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b>")
