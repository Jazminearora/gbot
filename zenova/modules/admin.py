from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler


def admin(update, context):
    buttons = [
        [
            InlineKeyboardButton("📥 Newsletter", callback_data='newsletter'),
            InlineKeyboardButton("✏️ Subscriptions", callback_data='subscriptions')
        ],
        [
            InlineKeyboardButton("👁️‍🗨️ Impressions", callback_data='impressions'),
            InlineKeyboardButton("📊 Statistics", callback_data='statistics')
        ],
        [
            InlineKeyboardButton("⛓ Referral link", callback_data='referral'),
            InlineKeyboardButton("👑 VIP Users", callback_data='vip_users')
        ],
        [
            InlineKeyboardButton("👥 List of users", callback_data='list_users'),
            InlineKeyboardButton("♿️ Delete inactive", callback_data='delete_inactive')
        ],
        [
            InlineKeyboardButton("🚫 Cancel", callback_data='cancel')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text('Please choose an option:', reply_markup=reply_markup)

def button_click(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'newsletter':
        query.edit_message_text(text="You selected Newsletter.")
    elif query.data == 'subscriptions':
        query.edit_message_text(text="You selected Subscriptions.")
    elif query.data == 'impressions':
        query.edit_message_text(text="You selected Impressions.")
    elif query.data == 'statistics':
        query.edit_message_text(text="You selected Statistics.")
    elif query.data == 'referral':
        query.edit_message_text(text="You selected Referral link.")
    elif query.data == 'vip_users':
        query.edit_message_text(text="You selected VIP Users.")
    elif query.data == 'list_users':
        query.edit_message_text(text="You selected List of users.")
    elif query.data == 'delete_inactive':
        query.edit_message_text(text="You selected Delete inactive.")
    elif query.data == 'cancel':
        query.edit_message_text(text="You canceled the operation.")

def main():
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("admin", admin))
    updater.dispatcher.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
