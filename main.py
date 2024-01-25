import logging
import telebot
from telebot import types
import datetime
import json
import sqlite3


# Configure logging
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='w', format='%(asctime)s - %(name)s - %(''levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot token from BotFather
bot_token = ''
bot = telebot.TeleBot(bot_token)

# Data storage
conn = sqlite3.connect('smile_bot.db', check_same_thread=False)


def setup_database():
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_smiles (
                user_id TEXT PRIMARY KEY,
                smiles TEXT
            )
        """)


setup_database()


def save_data(user_id, smiles):
    with conn:
        conn.execute("REPLACE INTO user_smiles (user_id, smiles) VALUES (?, ?)",
                     (user_id, json.dumps(smiles)))


def load_data(user_id):
    with conn:
        cur = conn.execute("SELECT smiles FROM user_smiles WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
        return []


def get_all_user_ids():
    with conn:
        cur = conn.execute("SELECT user_id FROM user_smiles")
        return [row[0] for row in cur.fetchall()]


# Function to send weekly message to users
def ask_weekly_smiles():
    user_ids = get_all_user_ids()  # Get all user IDs from the database
    for user_id in user_ids:
        markup = generate_markup()
        bot.send_message(user_id, "What smiles happened with you this week? 🗓", reply_markup=markup)


# Function to generate inline keyboard markup
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


# Function to send a welcome message with inline keyboard
def send_welcome(message):
    markup = generate_markup()
    msg = ("Hello! I'm your personal Smile recorder bot. 🤖\n"
           "Choose an option below to get started. 👇")
    bot.send_message(message.chat.id, msg, reply_markup=markup)


# Start command with a greeting and instructions
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = str(message.chat.id)
    user_smiles = load_data(user_id)  # Load this user's smiles from the database

    # If the user is not in the database, initialize their smiles list and save it
    if user_smiles is None:
        user_smiles = []
        save_data(user_id, user_smiles)

    send_welcome(message)


# Command to initiate adding a new smile
@bot.message_handler(commands=['addsmile'])
def add_smile_initiate(message):
    bot.send_message(message.chat.id, "What Smile would you like to record? 📝")
    bot.register_next_step_handler(message, add_smile_record)


# Function to record a new smile after user response
def add_smile_record(message):
    user_id = str(message.chat.id)
    user_smiles = load_data(user_id)  # Load only this user's smiles
    smile_text = message.text.strip()
    markup = generate_markup()

    if not smile_text:
        bot.send_message(message.chat.id, "You didn't specify Smile. Please try again using /addsmile. 🔁")
        return

    # Format the date as "23 January 2024"
    formatted_date = datetime.date.today().strftime("%d %B %Y")

    # Append the new smile to the user's existing smiles
    user_smiles.append({'date': formatted_date, 'smile': smile_text})

    # Save the updated smiles list for this user
    save_data(user_id, user_smiles)

    bot.reply_to(message, "Smile recorded successfully! ✅", reply_markup=markup)


def number_to_emoji(number):
    emoji_numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return ''.join(emoji_numbers[int(digit)] for digit in str(number))


# Command to show user smiles
@bot.message_handler(commands=['mysmiles'])
def show_smiles(message):
    user_id = str(message.chat.id)
    user_smiles = load_data(user_id)  # Load only this user's smiles

    if not user_smiles:
        bot.reply_to(message, "You have no recorded Smiles. 📭")
    else:
        response = "\n".join([f"{number_to_emoji(idx+1)} {smile['date']}: {smile['smile']}" for idx, smile in enumerate(user_smiles)])
        bot.reply_to(message, response)


# Command to update a smile
@bot.message_handler(commands=['updatesmile'])
def update_smile_prompt(message):
    user_id = str(message.chat.id)
    user_smiles = load_data(user_id)  # Load only this user's smiles

    if not user_smiles:
        bot.reply_to(message, "You have no recorded Smiles. 📭")
        return

    response = "Select a Smile to update by number: 📝 \n" + "\n".join(
        [f"{number_to_emoji(idx + 1)}: {smile['date']}: {smile['smile']}" for idx, smile in enumerate(user_smiles)])

    bot.send_message(message.chat.id, response)
    bot.register_next_step_handler(message, process_smile_update)


# Function to process the smile update
def process_smile_update(message):
    user_id = str(message.chat.id)
    user_smiles = load_data(user_id)  # Load smiles for this user

    try:
        parts = message.text.split(": ", 1)
        if len(parts) != 2:
            bot.reply_to(message, "Please enter a valid format: number: new details. 📝")
            return

        smile_number, new_details = parts
        smile_number = int(smile_number) - 1

        if 0 <= smile_number < len(user_smiles):
            user_smiles[smile_number]['smile'] = new_details
            save_data(user_id, user_smiles)  # Save the updated smiles for this user
            markup = generate_markup()
            bot.reply_to(message, "Smile updated successfully! ✏️✅", reply_markup=markup)
        else:
            bot.reply_to(message, "Invalid Smile number. 🚫 Please try again with valid Smile number.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid format: number: new details. 🔠")


# Command to delete a smile
@bot.message_handler(commands=['deletesmile'])
def delete_smile_prompt(message):
    user_id = str(message.chat.id)
    user_smiles = load_data(user_id)  # Load only this user's smiles

    if not user_smiles:
        bot.reply_to(message, "You have no recorded Smiles. 📭")
        return

    response = "Select a Smile to delete by number: 🗑️ \n" + "\n".join(
        [f"{number_to_emoji(idx + 1)}: {smile['date']}: {smile['smile']}" for idx, smile in enumerate(user_smiles)])

    bot.send_message(message.chat.id, response)
    bot.register_next_step_handler(message, process_smile_deletion)


# Function to process the smile deletion
def process_smile_deletion(message):
    user_id = str(message.chat.id)
    user_smiles = load_data(user_id)  # Load smiles for this user

    try:
        smile_number = int(message.text) - 1

        if 0 <= smile_number < len(user_smiles):
            del user_smiles[smile_number]
            save_data(user_id, user_smiles)  # Save the updated smiles for this user
            markup = generate_markup()
            bot.reply_to(message, "Smile deleted successfully! 🗑️✅", reply_markup=markup)
        else:
            bot.reply_to(message, "Invalid Smile number. 🚫 Please try again with valid Smile number.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid number. 🔢")


# Handle callback queries for inline keyboard buttons
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        if call.data == "add_smile":
            bot.answer_callback_query(call.id)
            logger.info("Callback: Add Smile button clicked")
            add_smile_initiate(call.message)

        elif call.data == "my_smiles":
            bot.answer_callback_query(call.id)
            logger.info("Callback: My Smiles button clicked")
            show_smiles(call.message)

        elif call.data == "update_smile":
            bot.answer_callback_query(call.id)
            logger.info("Callback: Update Smile button clicked")
            update_smile_prompt(call.message)

        elif call.data == "delete_smile":
            bot.answer_callback_query(call.id)
            logger.info("Callback: Delete Smile button clicked")
            delete_smile_prompt(call.message)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Error: {str(e)}")
        logger.exception("Exception in handle_callback_query")


# Helper function to list smiles and prompt for an action
def list_and_prompt_for_action(message, prompt, next_step_handler):
    user_id = str(message.chat.id)
    user_smiles = load_data(user_id)  # Load the smiles for this user from the database

    if not user_smiles:
        bot.reply_to(message, "You have no recorded Smiles. 📭")
        return

    response = prompt + "\n" + "\n".join([f"{idx+1}: {smile['date']}: {smile['smile']}" for idx, smile in enumerate(user_smiles)])
    bot.send_message(message.chat.id, response)
    bot.register_next_step_handler(message, next_step_handler)


# Generic message handler for any other text
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    markup = generate_markup()
    bot.send_message(message.chat.id, "Use the inline keyboard below to select a command:", reply_markup=markup)


# Start the bot
bot.polling()
