from pytz import timezone
from apscheduler.triggers.cron import CronTrigger

from database.premiumdb import get_top_chat_users
from database.chatdb import reset_chatime
from .. import cbot, scheduler
from helpers.translator import translate_async
from helpers.helper import find_language


async def weekly_gw():
    try:
        topper = get_top_chat_users()
        print(topper)

    except Exception as e:
        print( f"An error occured while distriburion of weekly gw: {e}" )

scheduler.add_job(weekly_gw, CronTrigger(day_of_week='sat', hour=20, minute=0), timezone=timezone('Europe/Moscow'))
# Schedule the task to run every 10 minutes
scheduler.add_job(weekly_gw, 'interval', minutes=1)