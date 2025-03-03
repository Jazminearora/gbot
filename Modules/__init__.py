import asyncio
import logging
import time
from importlib import import_module
from pymongo import MongoClient
from os import listdir, path
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.errors import ChatForbidden, ChatRestricted, PeerIdInvalid
import apscheduler.schedulers.asyncio as aps
from AaioAPI import AsyncAaioAPI
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI,  ADMINS as ADMIN_IDS, LOG_GROUP, REPORT_CHAT
from config import MERCHANT_ID, MERCHANT_KEY, API_KEY

# Tg bot __init_.py


loop = asyncio.get_event_loop()
load_dotenv()
boot = time.time()


logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)



cbot = Client(
    ":cbot:",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


client = MongoClient(MONGO_URI)
db = client["cboSot-psulimer"]
referdb = db["referdb"]
premiumdb = db["premiumb"]
mongodb = db["tgtobot"]
chatdb = db["chatdsd"]
residuedb = db["residuedb"]

# Create a async scheduler
scheduler = aps.AsyncIOScheduler()

aaio = AsyncAaioAPI(API_KEY, MERCHANT_KEY, MERCHANT_ID)

ADMIN_IDS = ADMIN_IDS
LOG_GROUP = LOG_GROUP
REPORT_CHAT = REPORT_CHAT

async def cbot_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await cbot.start()
    try:
        await cbot.send_message(int(LOG_GROUP), text= "Bot started successfully!")
    except (ChatRestricted, ChatForbidden):
        logger.warn("Please add to your log group, and give me administrator powers!")
    except PeerIdInvalid:
        logger.warn("Please add to your log group, and give me administrator powers!")
    getme = await cbot.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    if getme.last_name:
        BOT_NAME = getme.first_name + " " + getme.last_name
    else:
        BOT_NAME = getme.first_name
        

scheduler.start()
loop.run_until_complete(cbot_bot())