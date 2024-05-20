from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from .. import cbot, BOT_NAME, ADMIN_IDS, LOG_GROUP
from database.residuedb import BLuser, add_bluser, unblock_user
from database.premiumdb import save_premium_user


@cbot.on_message(filters.private & BLuser)
async def Banned_users_handler(client, msg: Message):
    txt = f"""
Hello,

Your account has been temporarily blocked for violating our community guidelines. 🚫 We've noticed inappropriate language in your messages, which is not tolerated on our platform. 🙅‍♂️

Please review our guidelines to ensure compliance upon your return. 📜 If you have any questions, feel free to contact our support team. 📧

Thank you for your cooperation. 🙏

Best regards,
{BOT_NAME} 💬
"""
    await msg.reply_text(txt)
    await msg.stop_propagation()

@cbot.on_message(filters.command("block") & filters.user(ADMIN_IDS))
async def block_user(client, msg: Message):
    try:
        if msg.reply_to_message:
            user_id = int(msg.reply_to_message.from_user.id)
            if user_id in ADMIN_IDS:
                await msg.reply("I can't ban my admins!!")
                return
            await add_bluser(user_id)
            await msg.reply("User blocked successfully!")
            return
        if len(msg.command) < 2:
            await msg.reply_text("Usage: /block <user id> or reply to a message")
            return
        user_id = int(msg.text.split(None, 1)[1])
        if user_id in ADMIN_IDS:
            await msg.reply("I can't ban my admins!!")
            return
        await add_bluser(int(user_id))
        await msg.reply("User blocked successfully!")
    except Exception as e:
        await msg.reply(f"Error: {e}")

@cbot.on_message(filters.command("unblock") & filters.user(ADMIN_IDS))
async def unblock_users(client, msg: Message):
    try:
        if msg.reply_to_message:
            user_id = msg.reply_to_message.from_user.id
            await unblock_user(int(user_id))
            await msg.reply("User unblocked successfully!")
            return
        if len(msg.command) < 2:
            await msg.reply_text("Usage: /unblock <user id> or reply to a message")
            return
        user_id = int(msg.text.split(None, 1)[1])
        await unblock_user(int(user_id))
        await msg.reply("User unblocked successfully!")
    except Exception as e:
        await msg.reply(f"Error: {e}")

@cbot.on_message(filters.command("mblock") & filters.user(ADMIN_IDS))
async def unblock_users_media(client, msg: Message):
    try:
        if msg.reply_to_message:
            user_id = msg.reply_to_message.from_user.id
            save_premium_user(user_id, block_media= True)
            await msg.reply("User blocked from sending media successfully!")
            return
        if len(msg.command) < 2:
            await msg.reply_text("Usage: /mblock <user id> or reply to a message")
            return
        user_id = int(msg.text.split(None, 1)[1])
        save_premium_user(user_id, block_media= True)
        await msg.reply("User blocked from sending media successfully!")
    except Exception as e:
        await msg.reply(f"Error: {e}")

@cbot.on_message(filters.command("munblock") & filters.user(ADMIN_IDS))
async def unblock_users_media(client, msg: Message):
    try:
        if msg.reply_to_message:
            user_id = msg.reply_to_message.from_user.id
            save_premium_user(user_id, block_media= False)
            await msg.reply("User unblocked from sending media successfully!")
            return
        if len(msg.command) < 2:
            await msg.reply_text("Usage: /munblock <user id> or reply to a message")
            return
        user_id = int(msg.text.split(None, 1)[1])
        save_premium_user(user_id, block_media= False)
        await msg.reply("User unblocked from sending media successfully!")
    except Exception as e:
        await msg.reply(f"Error: {e}")

@cbot.on_message(filters.command("unverify") & filters.user(ADMIN_IDS))
async def unblock_users_media(client, msg: Message):
    try:
        if msg.reply_to_message:
            user_id = msg.reply_to_message.from_user.id
            save_premium_user(user_id, verified= False)
            await msg.reply("User unverified successfully!")
            return
        if len(msg.command) < 2:
            await msg.reply_text("Usage: /unverify <user id> or reply to a message")
            return
        user_id = int(msg.text.split(None, 1)[1])
        save_premium_user(user_id, verified= False)
        await msg.reply("User unverified successfully!")
    except Exception as e:
        await msg.reply(f"Error: {e}")

@cbot.on_message(filters.command("verify") & filters.user(ADMIN_IDS))
async def unblock_users_media(client, msg: Message):
    try:
        if msg.reply_to_message:
            user_id = msg.reply_to_message.from_user.id
            save_premium_user(user_id, verified= True)
            await msg.reply("User verified successfully!")
            return
        if len(msg.command) < 2:
            await msg.reply_text("Usage: /verify <user id> or reply to a message")
            return
        user_id = int(msg.text.split(None, 1)[1])
        save_premium_user(user_id, verified= False)
        await msg.reply("User verified successfully!")
    except Exception as e:
        await msg.reply(f"Error: {e}")


@cbot.on_callback_query(filters.regex("extra_admin") & filters.user(ADMIN_IDS))
async def extra_admin(client, query: CallbackQuery):
    txt = """
👋 Hello Admins! 🛡️

📝 Here's a quick overview of the commands available:

✏️ /add_shear - Add a new word to the shear list (usage: /add_shear <word>)
Example: /add_shear NewWord

📋 /get_shear - Retrieve all shear words from the database
Example: /get_shear

🚫 /block - Block a user from the platform (usage: /block <user id> or reply to a message from the user)
Example: /block 123456789 or reply to the user's message to block them

🔓 /unblock - Unblock a user (usage: /unblock <user id> or reply to a message from the user)
Example: /unblock 123456789 or reply to the user's message to unblock them

🚫 /mblock - Block a user from sending media (usage: /mblock <user id> or reply to a message from the user)
Example: /mblock 123456789 or reply to the user's message to block media

🔓 /munblock - Unblock a user from sending media (usage: /munblock <user id> or reply to a message from the user)
Example: /munblock 123456789 or reply to the user's message to unblock media

✅ /verify - Verify a user (usage: /verify <user id> or reply to a message from the user)
Example: /verify 123456789 or reply to the user's message to verify them

❌ /unverify - Unverify a user (usage: /unverify <user id> or reply to a message from the user)
Example: /unverify 123456789 or reply to the user's message to unverify them
"""
    home_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
            InlineKeyboardButton(text="Close ❌", callback_data="st_close")]])

    await query.message.edit_text(txt, reply_markup= home_btn)