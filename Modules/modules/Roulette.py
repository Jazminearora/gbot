import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from uuid import uuid1

from helpers.helper import find_language
from helpers.filters import subscribed, user_registered
from helpers.translator import translate_async
from database.premiumdb import extend_premium_user_hrs
from database.residuedb import get_roulhist, store_roulette_history

from Modules import cbot , LOG_GROUP, ADMIN_IDS
from Modules.modules.buy_vip import aaio


@cbot.on_message(filters.command("roulette") & filters.private  & user_registered)
async def roulette_control(client, message):
    try:
        print("roulette")
        user_id = message.from_user.id
        user_lang = find_language(user_id)
        caption = await translate_async("In roulette you may get a subscription 💎 PREMIUM for a period of 6 hours to 5 months 🤯\n", user_lang)
        
        # Get the last 6 purchases from the database
        last_6_purchases = await get_roulhist(user_id)
        
        if last_6_purchases:
            history_caption = await translate_async("History of the last 6 spins:\n", user_lang)
            for i, purchase in enumerate(last_6_purchases, start=1):
                history_caption += f"{i}. {purchase}\n"
            caption += history_caption
        else:
            caption += await translate_async("You haven't purchased any roulette yet.\n", user_lang)
        
        caption += await translate_async("Try your luck quickly! 🎰", user_lang)
        
        button_text = await translate_async("Pay for roulette", user_lang)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, callback_data="roulette_pay")]])
        await message.reply_text(caption, reply_markup=markup)
    #handle except block
    except Exception as e:
        # log error
        await client.send_message(LOG_GROUP, f"Error in roulette_control: {e}")

@cbot.on_callback_query(filters.regex("roulette_pay"))
async def roulette_pay_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_lang = find_language(user_id)
    # Create a payment order
    order_id = str(uuid1())
    amount = 3
    if user_lang == "Azerbejani":
        lang = "au"
    elif user_lang == "Russian":
        lang = "ru"
    else:
        lang = "en"
    currency = "USD"
    desc = f"Roulette premium subscription for {user_id}"
    URL = await aaio.create_payment(order_id, amount, lang, currency, desc)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(await translate_async("💰 Proceed to payment", user_lang), url=URL)],
        [InlineKeyboardButton(await translate_async("🔄️ Check payment", user_lang), callback_data=f"check_roulette_payement_{order_id}")]
    ])
    await callback_query.message.edit_text(await translate_async("🎰 **Service:** Subscription Roulette\n💲 **Cost:** Only $3", user_lang), reply_markup=markup)

@cbot.on_callback_query(filters.regex("^check_roulette_payement_"))
async def check_roulette_payment_callback(_, callback_query):
    print("Check payment callback called")
    try:
        user_id = callback_query.from_user.id
        langauge = find_language(user_id)
        order_id = callback_query.data.split("_")[3]
        # Check the payment status using the order ID
        payment_info = await aaio.get_payment_info(order_id)
        # If the payment is successful, generate a random premium duration and extend the user's premium subscription
        if (payment_info and payment_info.is_success()) or user_id in ADMIN_IDS:
            durations = [6, 12, 24, 48, 72, 96, 120, 144, 168, 336, 504, 720, 1440, 2160, 2880, 3600 ]  # in hours
            duration_hours = random.choice(durations)
            extend_premium_user_hrs(user_id, duration_hours)
            duration_text = await get_premium_duration_text(duration_hours, langauge)
            await store_roulette_history(user_id, duration_text)
            await callback_query.message.delete()
            await callback_query.message.reply_text(await translate_async(f"Payment was successful. You got the premium for {duration_text} this time!", langauge))
            if user_id in ADMIN_IDS: #Just for testing
                await callback_query.message.reply_text("Just for testing purpose i have also added admin ids to verify for payment successfull. Once after checking tell me i will remove it.")
        else:
            await callback_query.answer(await translate_async("Payment is still pending.", langauge), show_alert=True)
    except Exception as e:
        await cbot.send_message(int(LOG_GROUP), f"ERROR!!\n\nAn error occured while checking the payment info!\nException:{e}\n\nUser ID:{user_id}\nOrder ID:{order_id}")
        await callback_query.message.reply_text(await translate_async("An error occured while validating the payment info. Reported successfully to my owner. If you have done payment, kindly visit to my owner and ask him to verify it manually and give your membership.", langauge))

async def get_premium_duration_text(duration_hours, language):
    if duration_hours < 24:
        return await translate_async(f"{duration_hours} hours", language)
    elif duration_hours < 168:
        return await translate_async(f"{duration_hours // 24} days", language)
    elif duration_hours < 720:
        return await translate_async(f"{duration_hours // 168} weeks", language)
    else:
        return await translate_async(f"{duration_hours // 720} months", language)
