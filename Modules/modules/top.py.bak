import re
from pyrogram import filters

from .. import cbot
from helpers.forcesub import subscribed, user_registered
from helpers.helper import find_language
from database.referdb import get_top_referers

button_pattern = re.compile(r"^(🔝 (Top|Лучшие|Ən yuxarı) 🔝)$")

@cbot.on_message(filters.private & filters.regex(button_pattern)  & subscribed & user_registered)
async def get_top(client, message):
    lang = find_language(message.from_user.id)
    top_referers = await get_top_referers()
    if top_referers:
        # Create a list of strings to store the top referers with their points
        top_referers_str = []
        # Iterate over the top referers and append their IDs and points to the list
        for i, (referer_id, points) in enumerate(top_referers, start=1):
            if i <= 5:
                top_referers_str.append(f"{i}. {client.get_users(referer_id).mention()} - {points} {get_points_text(lang)}")
        # Create a string to display the top referers
        top_referers_text = "\n".join(top_referers_str)
        # Send a message to the user with the top referers
        await message.reply(f"<b>{get_top_text(lang)}:</b>\n\n{top_referers_text}\n\n<b>{get_prize_text(lang)}</b>", parse_mode="html")
    else:
        # Send a message to the user if there are no top referers
        await message.reply(get_no_referers_text(lang), parse_mode="html")

def get_points_text(lang):
    if lang == "English":
        return "points"
    elif lang == "Russian":
        return "баллов"
    elif lang == "Azerbejani":
        return "nökbələri"

def get_top_text(lang):
    if lang == "English":
        return "Top Referers"
    elif lang == "Russian":
        return "Лучшие Рефералы"
    elif lang == "Azerbejani":
        return "Ən yaxşı referans verənlər"

def get_prize_text(lang):
    if lang == "English":
        return "Top referers get additional prizes like premium membership for free!"
    elif lang == " Russian":
        return "Лучшие рефералы получают дополнительные призы, такие как премиум-подписка бесплатно!"
    elif lang == "Azerbejani":
        return "Ən yaxşı referans verənlər premium üyvlİğİn daha ətraflı məlumatları üçün heç bir qiymətə qəbul edə bilərlər!"

def get_no_referers_text(lang):
    if lang == "English":
        return "There are no top referers yet. Keep inviting your friends to get rewards!"
    elif lang == "Russian":
        return "Пока нет лучших рефералов. Продолжайте приглашать своих друзей, чтобы получать награды!"
    elif lang == "Azerbejani":
        return "İndiyorlar mövcuddur. Dostlarınızı davam etmək üçün davet edin. Ödüllər almaq üçün!"