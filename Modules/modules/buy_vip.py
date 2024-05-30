from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from uuid import uuid1
import urllib.parse
from AaioAPI import AsyncAaioAPI

from helpers.helper import find_language
from helpers.filters import subscribed, user_registered
from helpers.translator import translate_async
from langdb.get_msg import get_premium_msg
from database.referdb import get_point
from database.premiumdb import extend_premium_user_hrs

from Modules import cbot , BOT_USERNAME, LOG_GROUP
from config import MERCHANT_ID, MERCHANT_KEY, API_KEY

aaio = AsyncAaioAPI(API_KEY, MERCHANT_KEY, MERCHANT_ID)


button_pattern = re.compile(r"^💎 (Premium|Премиум|Premium) 💎$")
@cbot.on_message((filters.regex(button_pattern)|filters.command("/vip")) & filters.private & subscribed & user_registered)
async def premium_option(client, message):
    user_id = message.from_user.id
    user_lang = find_language(user_id)
    caption, buttons = await get_premium_msg(user_lang)
    await message.reply_text(caption, reply_markup=buttons)

async def get_text(total_points, referral_link, language):
    msg = "Invite users using your link and receive 👑VIP status for 1 hour for each!\n\nInvited:"
    msg2 = "Your personal link:\n👉"
    share_txt = "Hey buddy!!\n\n Try this amazing bot for getting connected with strangers from the world!"
    
    translated_msg = await translate_async(msg, target_language=language)
    translated_msg2 = await translate_async(msg2, target_language=language)
    translated_share_txt = await translate_async(share_txt, target_language=language)
    
    message = (
        translated_msg + str(total_points) + "\n\n" +
        translated_msg2 + referral_link
    )
    return message, translated_share_txt

@cbot.on_callback_query(filters.regex("^prem_free$"))
async def premium_free_callback(bot, update):
    # Your logic here to handle the callback query
    user_id = update.from_user.id
    total_points = await get_point(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start=r{user_id}"
    
    user_lang = find_language(user_id)
    caption, share_txt = await get_text(total_points, referral_link, user_lang)
    
    encoded_share_txt = urllib.parse.quote(share_txt)
    share_link = f"https://t.me/share/url?text={encoded_share_txt}&url={referral_link}"
    
    refer_button_text = await translate_async("Refer your Friend", target_language=user_lang)
    
    await update.message.edit_text(
        text=caption,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(refer_button_text, url=share_link)]]
        )
    )

@cbot.on_message(filters.command(["referals", "sharelink"]) & filters.private & subscribed & user_registered)
async def referals_command(client, message):
    user_id = message.from_user.id
    total_points = await get_point(user_id)
    referral_link = f"https://t.me/{BOT_USERNAME}?start=r{user_id}"
    
    user_lang = find_language(user_id)
    caption , share_txt = await get_text(total_points, referral_link, user_lang)

    
    encoded_share_txt = urllib.parse.quote(share_txt)
    share_link = f"https://t.me/share/url?url={referral_link}&text={encoded_share_txt}"
    refer_button_text = await translate_async("Refer your Friend", target_language=user_lang)
    await message.reply_text(
        text=caption,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(refer_button_text, url=referral_link)]]
        )
    )

@cbot.on_callback_query(filters.regex(r"premium_"))
async def premium_callback(client, callback_query):
    user_id = callback_query.from_user.id
    language = find_language(user_id)
    data = callback_query.data
    if data == "premium_1_day":
        tex = await translate_async("1 day", language)
        amount = 1.08
        extend_hrs = 24
    elif data == "premium_3_days":
        tex = await translate_async("3 days", language)
        amount = 2.15
        extend_hrs = 72
    elif data == "premium_1_week":
        tex =await translate_async("1 week", language)
        amount = 8.61
        extend_hrs = 168
    elif data == "premium_1_month":
        tex =await translate_async("1 month", language)
        amount = 12.98
        extend_hrs = 720

    # Generate random order ID using UUID
    order_id = str(uuid1())
    if language == "Azerbejani":
        lang = "au"
    elif language == "Russian":
        lang = "ru"
    else:
        lang = "en"
    currency = "USD"  # You can get the user's currency here
    desc = f"Premium subscription for {extend_hrs} hrs. of {user_id}"  # You can get the description here

    URL = await aaio.create_payment(order_id, amount, lang, currency, desc)
    markup = InlineKeyboardMarkup([
    [InlineKeyboardButton(await translate_async("💰 Proceed to payment", language), url = URL)],
    [InlineKeyboardButton(await translate_async("🔄️ Check payment", language), callback_data=f"check_payement_{order_id}_{extend_hrs}")]])
    await callback_query.message.edit_caption(await translate_async(f"Order details:\n\nDuration: {tex}\nAmount: ${amount}\n\nPlease pay for your premium subscription!", language), reply_markup = markup)


@cbot.on_callback_query(filters.regex(r'check_payement_(.+)_(.+)'))
async def check_payment_callback(_, callback_query):
    try:
        user_id = callback_query.from_user.id
        langauge = find_language(user_id)
        order_id = callback_query.data.split("_")[2]
        hrs = callback_query.data.split("_")[3]
        # Check the payment status using the order ID
        payment_info = await aaio.get_payment_info(order_id)
        # If the payment is successful, extend the user's premium subscription
        if payment_info and payment_info.is_success():
            extend_premium_user_hrs(user_id, int(hrs))
            await callback_query.message.delete()
            await callback_query.message.reply_text(await translate_async("Payment was successful. Your premium subscription has been extended.", langauge))
        else:
            await callback_query.answer(await translate_async("Payment is still pending.", langauge), show_alert=True)
    except Exception as e:
        await cbot.send_message(LOG_GROUP, f"⚠️ERROR!!⚠️\n\nAn error occured while checking the payment info!\nException:{e}\n\nUser ID:{user_id}\nOrder ID:{order_id}")
        await callback_query.message.reply_text(await translate_async("An error occured while validating the payment info. Reported successfully to my owner. If you have done payment, kindly visit to my owner and ask him to verify it manually and give your membership.", langauge))
 