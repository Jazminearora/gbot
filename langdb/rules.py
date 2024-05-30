from Modules import BOT_USERNAME

async def get_rules(language):
    if language == "English":
        text= f"""
 Anonymous chat is a platform for communicating with people of different backgrounds and beliefs.  We want you to find a new and interesting person to talk to with every search.

 It’s unpleasant when, instead, users end up with an interlocutor whose goal is only to send you some link, ask you to buy something, send out some bad content, etc.

 Anonymous chat is created only for communication between two users.  You cannot use the chat to attract users to other resources, groups or chats, sell something, distribute it, etc.

 Through messages from the bot @{BOT_USERNAME} it is prohibited:
 — Identical messages asking to send something (money, etc.)
 — Ask to like in the chat
 — Throw any links you like at the beginning of the dialogue
 — Attract interlocutors to other resources, groups and chats
 — Send out phone numbers
 — Sell any services or things
 — Distribute child pornography in any form
 — Sell weapons, drugs, psychotropic substances
 — Send messages encouraging suicide
 — Send calls for riots
 — Send mournful messages
 — Post extremist content
 — Distribute pornography
 — Promote LGBT
 — Distribute and/or sell any other things, documents or information prohibited for distribution by law.

 If you break the rules you will be blocked
"""
    elif language == "Russian":
        text= f"""
Анонимный чат — это платформа для общения с людьми разного происхождения и убеждений.  Мы хотим, чтобы при каждом поиске вы находили нового и интересного человека для общения.

 Неприятно, когда вместо этого у пользователей оказывается собеседник, цель которого лишь отправить вам какую-то ссылку, попросить что-то купить, разослать плохой контент и т. д.

 Анонимный чат создан только для общения двух пользователей.  Вы не можете использовать чат для привлечения пользователей на другие ресурсы, группы или чаты, что-то продавать, распространять и т.п.

 Через сообщения бота @{BOT_USERNAME} запрещено:
 — Одинаковые сообщения с просьбой отправить что-либо (деньги и т. д.)
 — Попросить поставить лайк в чате
 — Кидайте любые понравившиеся ссылки в начало диалога
 — Привлекайте собеседников на другие ресурсы, группы и чаты
 — Отправьте номера телефонов
 — Продавать любые услуги или вещи
 — Распространять детскую порнографию в любой форме.
 — Продавать оружие, наркотики, психотропные вещества
 — Отправляйте сообщения, призывающие к самоубийству.
 — Призывы к беспорядкам
 — Отправляйте скорбные сообщения
 — Размещать экстремистский контент
 — Распространять порнографию
 — Продвигайте ЛГБТ
 — Распространять и/или продавать любые другие вещи, документы или информацию, запрещенные к распространению законодательством.

 Если вы нарушите правила, вас заблокируют
"""
    elif language == "Azerbejani":
        text= f"""
Anonim söhbət müxtəlif mənşəli və inanclı insanlarla ünsiyyət üçün platformadır.  İstəyirik ki, hər axtarışda danışa biləcəyiniz yeni və maraqlı insan tapın.

 Bunun əvəzinə istifadəçilərin məqsədi yalnız sizə hansısa link göndərmək, sizdən nəsə almaq istəmək, pis məzmun göndərmək və s. olan həmsöhbətlə rastlaşdıqda xoşagəlməz haldır.

 Anonim söhbət yalnız iki istifadəçi arasında ünsiyyət üçün yaradılır.  Siz istifadəçiləri digər resurslara, qruplara və ya söhbətlərə cəlb etmək, bir şey satmaq, yaymaq və s. üçün çatdan istifadə edə bilməzsiniz.

 @{BOT_USERNAME} botundan gələn mesajlar vasitəsilə bu qadağandır:
 — Bir şey göndərməyi tələb edən eyni mesajlar (pul və s.)
 — Çatda bəyənməyi xahiş edin
 — Dialoqun əvvəlində istədiyiniz linki atın
 — Həmsöhbətləri digər resurslara, qruplara və söhbətlərə cəlb edin
 - Telefon nömrələrini göndərin
 — İstənilən xidmət və ya əşyaları satmaq
 — Uşaq pornoqrafiyasını istənilən formada yaymaq
 — Silah, narkotik, psixotrop maddələr satmaq
 — İntihara təşviq edən mesajlar göndərin
 - İğtişaşlar üçün çağırışlar göndərin
 - Kədərli mesajlar göndərin
 - Ekstremist məzmun yerləşdirin
 - Pornoqrafiya yaymaq
 - LGBT-ni təbliğ edin
 — Qanunla yayılması qadağan olunmuş hər hansı digər əşyaları, sənədləri və ya məlumatları yaymaq və/və ya satmaq.

 Qaydaları pozsanız, bloklanacaqsınız
"""

    return text