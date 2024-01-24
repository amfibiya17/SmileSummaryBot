import logging
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='w', format='%(asctime)s - %(name)s - %(''levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot token from BotFather
bot_token = ''
bot = telebot.TeleBot(bot_token)

# Data storage (for simplicity, using a JSON file)
data_file = 'user_data.json'


def save_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file)


def load_data():
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# Load existing data
user_data = load_data()


# Function to send monthly message to users
def ask_weekly_events():
    for user_id in user_data.keys():
        markup = generate_markup()
        bot.send_message(user_id, "What events happened with you this week? 🗓", reply_markup=markup)


# Scheduler to ask users weekly on Sundays
scheduler = BackgroundScheduler()
scheduler.add_job(ask_weekly_events, 'cron', day_of_week='tue', hour=18, minute=00)
scheduler.start()


# Function to generate inline keyboard markup
def generate_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("Add Event 📝", callback_data="add_event"))
    markup.row(types.InlineKeyboardButton("My Events 📚", callback_data="my_events"))
    markup.row(types.InlineKeyboardButton("Update Event ✏️", callback_data="update_event"))
    markup.row(types.InlineKeyboardButton("Delete Event 🗑️", callback_data="delete_event"))
    return markup


# Function to send a welcome message with inline keyboard
def send_welcome(message):
    markup = generate_markup()
    msg = ("Hello! I'm your personal event recorder bot. 🤖\n"
           "Choose an option below to get started. 👇")
    bot.send_message(message.chat.id, msg, reply_markup=markup)


# Start command with a greeting and instructions
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = str(message.chat.id)
    if user_id not in user_data:
        user_data[user_id] = []
        save_data(user_data)

    send_welcome(message)


# Command to initiate adding a new event
@bot.message_handler(commands=['addevent'])
def add_event_initiate(message):
    bot.send_message(message.chat.id, "What event would you like to record? 📝")
    bot.register_next_step_handler(message, add_event_record)


# Function to record a new event after user response
def add_event_record(message):
    user_id = str(message.chat.id)
    event_text = message.text.strip()
    markup = generate_markup()

    if not event_text:
        bot.send_message(message.chat.id, "You didn't specify an event. Please try again using /addevent. 🔁")
        return

    # Format the date as '23 January 2024'
    formatted_date = datetime.date.today().strftime("%d %B %Y")

    user_data[user_id].append({'date': formatted_date, 'event': event_text})
    save_data(user_data)
    bot.reply_to(message, "Event recorded successfully! ✅", reply_markup=markup)


def number_to_emoji(number):
    emoji_numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return ''.join(emoji_numbers[int(digit)] for digit in str(number))


@bot.message_handler(commands=['myevents'])
def show_events(message):
    current_user_data = load_data()

    user_id = str(message.chat.id)
    events = current_user_data.get(user_id, [])

    if not events:
        bot.reply_to(message, "You have no recorded events. 📭")
    else:
        response = "\n".join([f"{number_to_emoji(idx+1)} {event['date']}: {event['event']}" for idx, event in enumerate(events)])
        bot.reply_to(message, response)


# Command to update an event
@bot.message_handler(commands=['updateevent'])
def update_event_prompt(message):
    list_and_prompt_for_action(message, "Select an event to update by number: 📝 \n", process_event_update)


# Function to process the event update
def process_event_update(message):
    user_id = str(message.chat.id)
    try:
        parts = message.text.split(": ", 1)
        if len(parts) != 2:
            bot.reply_to(message, "Please enter a valid format: number: new details. 📝")
            return

        event_number, new_details = parts
        event_number = int(event_number) - 1
        current_user_data = load_data()

        if not new_details:
            bot.reply_to(message, "Event details cannot be empty. 🚫 Please try again.")
            return

        if 0 <= event_number < len(current_user_data.get(user_id, [])):
            current_user_data[user_id][event_number]['event'] = new_details
            save_data(current_user_data)
            bot.reply_to(message, "Event updated successfully! ✏️✅")
        else:
            bot.reply_to(message, "Invalid event number. 🚫 Please try again with a valid event number.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid format: number: new details. 🔠")


# Command to delete an event
@bot.message_handler(commands=['deleteevent'])
def delete_event_prompt(message):
    list_and_prompt_for_action(message, "Select an event to delete by number: 🗑️ \n", process_event_deletion)


# Function to process the event deletion
def process_event_deletion(message):
    user_id = str(message.chat.id)
    try:
        event_number = int(message.text) - 1
        current_user_data = load_data()

        if 0 <= event_number < len(current_user_data.get(user_id, [])):
            del current_user_data[user_id][event_number]
            save_data(current_user_data)
            bot.reply_to(message, "Event deleted successfully! 🗑️✅")
        else:
            bot.reply_to(message, "Invalid event number. 🚫 Please try again with a valid event number.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid number. 🔢")


# Handle callback queries for inline keyboard buttons
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    try:
        if call.data == "add_event":
            bot.answer_callback_query(call.id)
            logger.info("Callback: Add Event button clicked")
            add_event_initiate(call.message)

        elif call.data == "my_events":
            bot.answer_callback_query(call.id)
            logger.info("Callback: My Events button clicked")
            show_events(call.message)

        elif call.data == "update_event":
            bot.answer_callback_query(call.id)
            logger.info("Callback: Update Event button clicked")
            update_event_prompt(call.message)

        elif call.data == "delete_event":
            bot.answer_callback_query(call.id)
            logger.info("Callback: Delete Event button clicked")
            delete_event_prompt(call.message)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Error: {str(e)}")
        logger.exception("Exception in handle_callback_query")


# Helper function to list events and prompt for an action
def list_and_prompt_for_action(message, prompt, next_step_handler):
    user_id = str(message.chat.id)
    events = user_data.get(user_id, [])
    if not events:
        bot.reply_to(message, "You have no recorded events. 📭")
        return

    response = prompt + "\n" + "\n".join([f"{idx+1}: {event['date']}: {event['event']}" for idx, event in enumerate(events)])
    bot.send_message(message.chat.id, response)
    bot.register_next_step_handler(message, next_step_handler)


# Generic message handler for any other text
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    markup = generate_markup()
    bot.send_message(message.chat.id, "Use the inline keyboard below to select a command:", reply_markup=markup)


# Start the bot
bot.polling()
