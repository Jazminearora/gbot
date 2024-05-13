from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import pyrostep

from Modules import cbot, BOT_USERNAME
from database.referdb import create_refer_program, delete_refer_program, get_refer_programs_data

pyrostep.listen(cbot)

@cbot.on_callback_query(filters.regex('referral_admin'))
async def referral_admin(_, callback_query):
    # Get the current active refer programs
    programs = await get_refer_programs_data()
    
    # Create a string to display the program names and total points
    program_str = ""
    for index, program in enumerate(programs, start=1):
        program_name = program['name']
        program_id = program['id']
        total_points = program['points']
        refer_link = f"https://t.me/{BOT_USERNAME}?start=r{program_id}"
        
        program_details = (
            f"🔹 {index}. Program name: {program_name}\n"
            f"     🆔 ID: {program_id}\n"
            f"     🔢 Total Points: {total_points}\n"
            f"     🔗 Refer link: {refer_link}\n\n"
        )
        program_str += program_details
    
    # Create an InlineKeyboardMarkup with buttons for adding and deleting programs
    program_buttons = [
        [
            InlineKeyboardButton("📊 Add program", callback_data='add_program'),
            InlineKeyboardButton("🗑️ Delete program", callback_data='delete_program')
        ],
        [
            InlineKeyboardButton(text="Back 🔙", callback_data="st_back"),
            InlineKeyboardButton(text="Close ❌", callback_data="st_close")
        ]
    ]
    program_markup = InlineKeyboardMarkup(program_buttons)
    
    # Send a message with the program details and the program buttons
    await callback_query.message.edit_text(f"Current active refer programs:\n\n{program_str}", reply_markup=program_markup)

# Callback handler for add_program
@cbot.on_callback_query(filters.regex('add_program'))
async def add_program(_, callback_query):
    try:
        # Ask the admin to enter the program name
        await callback_query.message.reply_text(text="Please enter the new program name:")
        program_name = await pyrostep.wait_for(callback_query.from_user.id)
        
        # Ask the admin to enter the admin and chat IDs
        await callback_query.message.reply_text(text="Please enter the users/chat IDs where I will report on new joining. Provide one ID per line:")
        admin_chat_ids_input = await pyrostep.wait_for(callback_query.from_user.id)
        try:
            # Split the input by newline character to create a list of IDs
            admin_list = [(id) for id in admin_chat_ids_input.text.split('\n') if id.strip()]
        except ValueError:
            await callback_query.message.reply_text("Its seems you didn't provided admins id in correct format.")          
        print(admin_list)
    except TimeoutError:
        await callback_query.message.reply_text("OHOO, Timeout error! Please retry again.")
        return
    try:
        if not admin_list or program_name.text:
            await callback_query.message.reply_text("OHOO, Timeout error! Please retry again.")
            return
        # Create the new refer program
        program_id = await create_refer_program(admin_ids= admin_list, promotion_name= program_name.text)
    except Exception as r:
        await callback_query.message.edit_text(text=f"An error occured!\n\n{r}")
    # Send a message to the admin with the program ID
    await callback_query.message.reply_text(f"Refer program '{program_name.text}' created with ID {program_id}")

# Callback handler for delete_program
@cbot.on_callback_query(filters.regex('delete_program'))
async def delete_program(_, callback_query):


    # Ask the admin to enter the program ID
    await callback_query.message.reply_text(text="Please enter the program ID:")
    program_id = await pyrostep.wait_for(callback_query.from_user.id)
    # Delete the refer program with the given ID
    await delete_refer_program(int(program_id.text))
    # Send a message to the admin with the program ID
    await callback_query.message.reply_text(f"Refer program with ID {program_id.text} deleted")
