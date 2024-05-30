async def get_help_msg(language):
    print(language)
    if language == "English":
        text= """
An anonymous chat bot that will find interlocutors for anonymous communication based on interests and gender.

Available commands:

/start - start the dialogue
/help - show this message
/vip - 👑Details about VIP
/profile - view or change your profile
/rules - chat and ban rules
/frens - Get your friend list
/top - Weekly chat top users menu

/next - next person
/search - search interlocutor
/stop - ends the dialogue
/sharelink - Send a link or link to your Telegram account

All commands are always available via the "Menu" button at the bottom left of the screen
In chats, you can send me text, links, GIFs, stickers, photos, videos, or voice messages, and I'll anonymously forward them to your interlocutor.
"""

    elif language == "Russian":
        text= """
Анонимный чат бот, который ищет собеседников для анонимной общения на основе интересов и пола.

Доступные команды:

/start - начать диалог
/help - показать этот сообщение
/vip - 👑Детали VIP
/profile - просмотр или изменение профиля
/rules - правила чата и бан
/frens - Получить список друзей
/top - Рейтинг чата пользователей

/next - следующий пользователь
/search - поиск собеседника
/stop - закончить диалог
/sharelink - Отправить ссылку или ссылку на ваш аккаунт в Telegram

Все команды всегда доступны через кнопку «Меню» в нижнем левом углу экрана.
В чатах вы можете отправлять мне текст, ссылки, GIF, стикеры, фотографии, видео или голосовые сообщения, и я анонимно перешлю их вашему собеседнику.
"""
    elif language == "Azerbejani":
        text= """
Anonim söhbət botu maraqlarınıza və cinsinizə əsaslanaraq anonim ünsiyyət üçün həmsöhbətlər tapacaq.

Mövcud komandalar:

/start - dialoqu başlat
/help - bu mesajı göstər
/vip - 👑VIP haqqında ətraflı məlumat
/profile - profilinizi görüntüləyin və ya dəyişdirin
/rules - söhbət və ban qaydaları
/frens - dost siyahınızı əldə edin
/top - Həftəlik söhbət ən yaxşı istifadəçilər menyusu

/next - növbəti şəxs
/search - həmsöhbət axtar
/stop - dialoqu bitir
/sharelink - Link və ya Telegram hesabınızın linkini göndərin

Bütün komandalar həmişə ekranın sol alt küncündəki "Menyu" düyməsi vasitəsilə mövcuddur
Söhbətlərdə mənə mətn, linklər, GIF, stikerlər, şəkillər, videolar və ya səsli mesajlar göndərə bilərsiniz və mən onları anonim şəkildə həmsöhbətinizə yönləndirəcəyəm.
"""
    else:
        text = None

    return text