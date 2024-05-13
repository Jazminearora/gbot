import asyncio
import importlib
from pyrogram import idle
from Modules import cbot, mongodb
from Modules.modules import ALL_MODULES
from config import key
from pyrogram import filters

loop = asyncio.get_event_loop()

data = {
    "database": {
        "English": [],
        "Russian": [],
        "Azerbejani": [],
        "male": [],
        "female": [],
        "below_18": [],
        "18_24": [],
        "25_34": [],
        "above_35": [],
        "communication": [],
        "intimacy": [],
        "selling": [],
        "movies": [],
        "anime": []
    }
}


#Store data in the collection
inserted_id = mongodb.insert_one({key: data}).inserted_id
print("Data stored successfully with id:", inserted_id)

async def cbot_boot():
    for all_module in ALL_MODULES:
        importlib.import_module("Modules.modules." + all_module)
    print("𝖻𝗈𝗍 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎lly 𝗌𝗍𝖺𝗋𝗍")
    await idle()


@cbot.on_message(filters.command("restart"))
async def restart_bot(client, message):
    await message.reply("Restarting bot...")
    await asyncio.sleep(1)
    stop_task = loop.create_task(client.stop())
    await cbot_boot()
    await stop_task


    
if __name__ == "__main__":
    loop.run_until_complete(cbot_boot())
    