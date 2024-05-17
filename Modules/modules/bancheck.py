from pyrogram import filters
from pyrogram.types import Message
from .. import cbot, BOT_NAME, ADMIN_IDS, LOG_GROUP
from database.residuedb import BLuser, add_bluser, unblock_user

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
