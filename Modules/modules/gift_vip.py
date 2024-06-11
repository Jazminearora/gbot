from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import re
from uuid import uuid1
import urllib.parse

from helpers.helper import find_language
from helpers.filters import subscribed, user_registered
from helpers.translator import translate_async
from langdb.get_msg import gift_premium_msg
from database.premiumdb import extend_premium_user_hrs, vip_users_details

from Modules import cbot , BOT_USERNAME, LOG_GROUP, aaio


# @cbot.on_callback_query(filters.regex("^gift_fren_"))
# async def premium_bsck(client, query: CallbackQuery):
#     user_id = query.from_user.id
#     friend_id = int(query.data.split("_")[2])
#     user_lang = find_language(user_id)
#     caption, buttons = await gift_premium_msg(friend_id, user_lang)
#     await query.message.reply(caption, reply_markup=buttons)

@cbot.on_callback_query(filters.regex(r"frx_"))
async def premium_callback(client, callback_query: CallbackQuery):
    data = callback_query.data
    try:
        user_id = callback_query.from_user.id
        friend_id = int(callback_query.data.split("_")[1])
        language = find_language(user_id)
        if data == f"frx_{friend_id}_1_day":
            tex = await translate_async("1 day", language)
            amount = 1.08
            extend_hrs = 24
        elif data == f"frx_{friend_id}_3_days":
            tex = await translate_async("3 days", language)
            amount = 2.15
            extend_hrs = 72
        elif data == f"frx_{friend_id}_wek":
            tex = await translate_async("1 week", language)
            amount = 8.61
            extend_hrs = 168
        elif data == f"frx_{friend_id}_mnt":
            tex = await translate_async("1 month", language)
            amount = 12.98
            extend_hrs = 720
        else:
            await callback_query.message.edit_caption(await translate_async(f"Invalid option selected.: {data}", language))
            return

        # Generate random order ID using UUID
        order_id = str(uuid1())
        if language == "Azerbejani":
            lang = "au"
        elif language == "Russian":
            lang = "ru"
        else:
            lang = "en"
        currency = "USD"  # You can get the user's currency here
        desc = f"Gift of Premium subscription for {extend_hrs} hrs. to {friend_id} by {user_id}"  # You can get the description here

        URL = await aaio.create_payment(order_id, amount, lang, currency, desc)
        if not URL:
            await callback_query.message.edit_caption(await translate_async("Failed to create payment URL.", language))
            return

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(await translate_async("💰 Proceed to payment", language), url=URL)],
            [InlineKeyboardButton(await translate_async("🔄️ Check payment", language), callback_data=f"gift_payement_{order_id}_{extend_hrs}_{friend_id}")]
        ])
        await callback_query.message.edit_caption(await translate_async(f"Order details:\n\nDuration: {tex}\nAmount: ${amount}\n\nPlease pay for gifting premium subscription to your friend!", language), reply_markup=markup)

    except Exception as e:
        await callback_query.message.edit_caption(await translate_async("An error occurred. Please try again later.", language))
        print(f"Error: {e}", data)
@cbot.on_callback_query(filters.regex(r'gift_payement_(.+)_(.+)_(.+)'))
async def check_payment_callback(_, callback_query):
    try:
        user_id = callback_query.from_user.id
        langauge = find_language(user_id)
        order_id = callback_query.data.split("_")[2]
        hrs = callback_query.data.split("_")[3]
        friend_id = int(callback_query.data.split("_")[4])
        # Check the payment status using the order ID
        payment_info = await aaio.get_payment_info(order_id)
        # If the payment is successful, extend the user's premium subscription
        if payment_info and payment_info.is_success():
            extend_premium_user_hrs(friend_id, int(hrs))
            frens_list = vip_users_details(friend_id, "frens")
            for friend_id in frens_list:
                name = friend_id["nickname"]
            await callback_query.message.delete()
            await cbot.send_message(friend_id, f"{await translate_async(f"You have recieved premium subscription for {hrs} hours from", target_language= find_language(friend_id))} {name}.")
            await callback_query.message.reply_text(await translate_async("Payment was successful. Your friend has received premium subscription.", langauge))
        else:
            await callback_query.answer(await translate_async("Payment is still pending.", langauge), show_alert=True)
    except Exception as e:
        await cbot.send_message(int(LOG_GROUP), f"⚠️ERROR!!⚠️\n\nAn error occured while checking the payment info!\nException:{e}\n\nUser ID:{user_id}\nOrder ID:{order_id}")
        await callback_query.message.reply_text(await translate_async("An error occured while validating the payment info. Reported successfully to my owner. If you have done payment, kindly visit to my owner and ask him to verify it manually and give your membership.", langauge))
 