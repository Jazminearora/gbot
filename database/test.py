from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Sample data similar to your provided data
data = {
    "id": 4716,
    "text": "Sample message",
    "reply_markup": {
        "inline_keyboard": [
            [{"text": "Old Button", "url": "https://example.com/old_button"}]
        ]
    }
}

# Define the new button to append
new_button = {"text": "New Button", "url": "https://example.com/new_button"}

# Append the new button to the existing inline keyboard markup
if "reply_markup" not in data or "inline_keyboard" not in data["reply_markup"]:
    data["reply_markup"] = {"inline_keyboard": []}

data["reply_markup"]["inline_keyboard"].append([new_button])

# Print the updated data
print(data)
