import asyncio
import logging
import time
from importlib import import_module
from pymongo import MongoClient
from os import listdir, path
from dotenv import load_dotenv
from pyrogram import Client
from pyrogram.errors import ChatRestricted, ChatForbidden
import apscheduler.schedulers.asyncio as aps
from config import API_ID, API_HASH, BOT_TOKEN, BOT_USERNAME, MONGO_URI,  ADMINS as ADMIN_IDS, LOG_GROUP

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
db = client["zenova-xy"]
referdb = db["referdb"]
premiumdb = db["premiumb"]
mongodb = db["tgtbot"]
chatdb = db["chatdsd"]

# Create a async scheduler
scheduler = aps.AsyncIOScheduler()

ADMIN_IDS = ADMIN_IDS

async def cbot_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await cbot.start()
    getme = await cbot.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    try:
        await cbot.send_message(LOG_GROUP, text= "Bot started successfully!")
    except (ChatRestricted, ChatForbidden):
        logger.critical("Please add me to your log group and give me administrator power!")
    except Exception as e:
        logger.critical(f"An error occured while starting the bot!\nError:{e}\n\nPlease make sure LOG_GROUP is valid add also me to your log group and give me administrator power!")
    if getme.last_name:
        BOT_NAME = getme.first_name + " " + getme.last_name
    else:
        BOT_NAME = getme.first_name

scheduler.start()
loop.run_until_complete(cbot_bot())
