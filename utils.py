from telebot import types


def number_to_emoji(number):
    emoji_numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return ''.join(emoji_numbers[int(digit)] for digit in str(number))


def generate_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Add Smile 📝", callback_data="add_smile"),
        types.InlineKeyboardButton("My Smiles 📚", callback_data="my_smiles")
    )
    markup.row(
        types.InlineKeyboardButton("Update Smile ✏️", callback_data="update_smile"),
        types.InlineKeyboardButton("Delete Smile 🗑️", callback_data="delete_smile")
    )
    return markup
