from pytz import timezone
from apscheduler.triggers.cron import CronTrigger

from database.premiumdb import get_top_chat_users, extend_premium_user_hrs
from database.chatdb import reset_chatime
from .. import cbot, scheduler
from helpers.translator import translate_async, translate_text
from helpers.helper import find_language


async def weekly_gw():
    try:
        topper = get_top_chat_users()

        # Distribute premium to top 3 users
        for i, user in enumerate(topper):
            user_id = user['user_id']
            print(user_id)
            chat_time = user['chat_time']

            # Distribute premium based on the rank
            if i == 0:
                days = 3
            elif i == 1:
                days = 2
            elif i == 2:
                days = 1

            # Extend the user's premium subscription
            extend_premium_user_hrs(int(user_id), days * 24)

            place = '1st' if i == 0 else '2nd' if i == 1 else '3rd'
            # Notify the user about their reward
            message = f"🏆 Congratulations, you won the weekly giveaway! 🏆\n\n"
            message += f"🥇 Prizes:\n"
            message += f"🥇 {place} place - free subscription for {days} days\n\n"
            message += f"🎉 You won {'1st' if i == 0 else '2nd' if i == 1 else '3rd'} place with {chat_time} chat time!\n\n"
            message += "🎉 Enjoy your free subscription! 🎉"

            # Translate the message to the user's language
            user_language = find_language(int(user_id))
            try:
                translated_message = await translate_async(message, user_language)
            except Exception as e:
                translated_message = f"Error occurred during translation: {e}"
                print(f"Error occurred during translation for user {user_id}: {e}")
            # Send the message to the user
            await cbot.send_message(user_id, text = translated_message)
        # Reset the user's chat time
        reset_chatime()

    except Exception as e:
        print( f"An error occured while distributing weekly gw: {e}" )

scheduler.add_job(weekly_gw, CronTrigger(day_of_week='sat', hour=20, minute=0), timezone=timezone('Europe/Moscow'))


 # for testing purpose
scheduler.add_job(weekly_gw, 'interval', minutes=2)