from pytz import timezone
from pyrogram.errors import PeerIdInvalid
from datetime import timedelta
from apscheduler.triggers.cron import CronTrigger

from database.premiumdb import get_top_chat_users, extend_premium_user_hrs
from database.chatdb import reset_chatime
from .. import cbot, scheduler
from helpers.translator import translate_async
from helpers.helper import find_language
from config import LOG_GROUP


# async def weekly_gw():
#     try:
#         topper = get_top_chat_users()
#         st_win1 = {}
#         st_win2 = {}
#         st_win3 = {}
#         formatted_chat_time = str(timedelta(seconds=user["chat_time"]))
#         # Distribute premium to top 3 users
#         for i, user in enumerate(topper):
#             user_id = user['user_id']
#             print(user_id)
#             chat_time = user['chat_time']

#             # Distribute premium based on the rank
#             if i == 0:
#                 days = 3
#                 st_win1.update({"user_id": user_id, "chat_time":chat_time})
#             elif i == 1:
#                 days = 2
#                 st_win2.update({"user_id": user_id, "chat_time":chat_time})
#             elif i == 2:
#                 days = 1
#                 st_win3.update({"user_id": user_id, "chat_time":chat_time})

#             # Extend the user's premium subscription
#             extend_premium_user_hrs(int(user_id), days * 24)

#             place = '1st' if i == 0 else '2nd' if i == 1 else '3rd'
#             # Notify the user about their reward
#             message = f"🏆 Congratulations, you won the weekly giveaway! 🏆\n\n"
#             message += f"🥇 Prizes:\n"
#             message += f"🥇 {place} place - free subscription for {days} days\n\n"
#             message += f"🎉 You won {'1st' if i == 0 else '2nd' if i == 1 else '3rd'} place with {chat_time} chat time!\n\n"
#             message += "🎉 Enjoy your free subscription! 🎉"

#             # Translate the message to the user's language
#             user_language = find_language(int(user_id))
#             try:
#                 translated_message = await translate_async(message, user_language)
#             except Exception as e:
#                 translated_message = f"Error occurred during translation: {e}"
#                 print(f"Error occurred during translation for user {user_id}: {e}")
#             try:
#                 # Send the message to the user
#                 await cbot.send_message(int(user_id), text = translated_message)
#             except PeerIdInvalid:
#                 retry = await cbot.send_message(LOG_GROUP, text= translated_message)
#                 try:
#                     await retry.copy(int(user_id))
#                 except:
#                     await cbot.send_message(LOG_GROUP, text= f"{e}\n\nError occured in sending winning message to winner! Premium membership activated for the user! User details-\n\nUser id = {user_id}\nPosition = {place}\nChat time = {chat_time}")
#                     pass
#                 await retry.delete()
#             except Exception as e:
#                 await cbot.send_message(LOG_GROUP, text= f"{e}\n\nError occured in sending winning message to winner! Premium membership activated for the user! User details-\n\nUser id = {user_id}\nPosition = {place}\nChat time = {chat_time}")
#                 pass
#         # send a message to log group about weekly winners  
#         await cbot.send_message(LOG_GROUP, f"**WEEKLY WINNER ANNOUNCEMENT**\n\n--1st Position--\nUser_id: {st_win1.get("user_id")}\nWeek chat time:{st_win1.get("chat_time")}\n\n--2nd Position--\nUser_id: {st_win2.get("user_id")}\nWeek chat time:{st_win2.get("chat_time")}\n\n--3rd Position--\nUser_id: {st_win3.get("user_id")}\nWeek chat time:{st_win3.get("chat_time")}")
#         # Reset the user's chat time
#         reset_chatime()

#     except Exception as e:
#         print( f"An error occured while distributing weekly gw: {e}" )



async def weekly_gw():
    try:
        topper = get_top_chat_users()
        winners = [{"user_id": None, "chat_time": None} for _ in range(3)]

        for i, user in enumerate(topper):
            user_id = user['user_id']
            chat_time = user['chat_time']

            # Distribute premium based on the rank
            days = 3 if i == 0 else 2 if i == 1 else 1
            winners[i] = {"user_id": user_id, "chat_time": chat_time}

            # Extend the user's premium subscription
            extend_premium_user_hrs(int(user_id), days * 24)

            place = '1st' if i == 0 else '2nd' if i == 1 else '3rd'
            # Notify the user about their reward
            message = construct_message(place, days, chat_time)
            user_language = find_language(int(user_id))
            translated_message = await translate_async(message, user_language)
            await send_message(int(user_id), translated_message, LOG_GROUP, place, chat_time)

        # send a message to log group about weekly winners
        await send_weekly_winner_announcement(LOG_GROUP, winners)

        # Reset the user's chat time
        reset_chatime()

    except Exception as e:
        print(f"An error occurred while distributing weekly gw: {e}")


def construct_message(place, days, chat_time):
    message = f"🏆 Congratulations, you won the weekly giveaway! 🏆\n\n"
    message += f"🥇 Prizes:\n"
    message += f"🥇 {place} place - free subscription for {days} days\n\n"
    message += f"🎉 You won {place} place with {chat_time} chat time!\n\n"
    message += "🎉 Enjoy your free subscription! 🎉"
    return message


async def send_message(user_id, message, log_group, place, chat_time):
    try:
        await cbot.send_message(user_id, text=message)
    except PeerIdInvalid:
        retry = await cbot.send_message(log_group, text=message)
        try:
            await retry.copy(user_id)
        except:
            await cbot.send_message(log_group, text=f"Error occurred in sending winning message to winner! Premium membership activated for the user! User details-\n\nUser id = {user_id}\nPosition = {place}\nChat time = {chat_time}")
            pass
        await retry.delete()
    except Exception as e:
        await cbot.send_message(log_group, text=f"{e}\n\nError occurred in sending winning message to winner! Premium membership activated for the user! User details-\n\nUser id = {user_id}\nPosition = {place}\nChat time = {chat_time}")


async def send_weekly_winner_announcement(log_group, winners):
    message = "🏆 **WEEKLY CHAMPIONS ANNOUNCEMENT** 🏆\n\n"
    message += f"**1st Place**\n"
    message += f"🥇 User_id: {winners[0].get('user_id')}\n"
    message += f"🕒 Weekly Chat Time: {winners[0].get('chat_time')}\n\n"
    message += f"**2nd Place**\n"
    message += f"🥈 User_id: {winners[1].get('user_id')}\n"
    message += f"🕒 Weekly Chat Time: {winners[1].get('chat_time')}\n\n"
    message += f"**3rd Place**\n"
    message += f"🥉 User_id: {winners[2].get('user_id')}\n"
    message += f"🕒 Weekly Chat Time: {winners[2].get('chat_time')}\n\n"
    message += "Congratulations to all winners! Let's keep the momentum going! 💪🎉"
    await cbot.send_message(log_group, message)

scheduler.add_job(weekly_gw, CronTrigger(day_of_week='sat', hour=20, minute=0), timezone=timezone('Europe/Moscow'))


 # for testing purpose
scheduler.add_job(weekly_gw, 'interval', minutes=2)