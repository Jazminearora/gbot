import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from uuid import uuid1

from helpers.helper import find_language
from helpers.filters import user_registered
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
        [InlineKeyboardButton(await translate_async("🔄️ Check payment", user_lang), callback_data=f"test_rand_reciept_{order_id}")]
    ])
    await callback_query.message.edit_text(await translate_async("🎰 **Service:** Subscription Roulette\n💲 **Cost:** Only $3", user_lang), reply_markup=markup)
