import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import json

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
def ask_monthly_events():
    for user_id in user_data.keys():
        bot.send_message(user_id, "What events happened with you this month? You can record them using /addevent")

# Scheduler to ask users monthly
scheduler = BackgroundScheduler()
scheduler.add_job(ask_monthly_events, 'cron', day=1, hour=0, minute=0)
scheduler.start()

# Function to send a welcome message
def send_welcome(message):
    msg = ("Hello! I'm your personal event recorder bot.\n\n"
           "• Use /addevent to record a new event.\n"
           "• Use /myevents to see your recorded events.\n"
           "• Use /deleteevent to delete an event.\n"
           "• Use /updateevent to update an event.\n\n"
           "What would you like to do?")
    bot.reply_to(message, msg)

# Start command with a greeting and instructions
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        user_data[user_id] = []
        save_data(user_data)
    send_welcome(message)

# Command to initiate adding a new event
@bot.message_handler(commands=['addevent'])
def add_event_initiate(message):
    bot.send_message(message.chat.id, "What event would you like to record?")
    bot.register_next_step_handler(message, add_event_record)

# Function to record a new event after user response
def add_event_record(message):
    user_id = str(message.from_user.id)
    event_text = message.text.strip()

    if not event_text:
        bot.send_message(message.chat.id, "You didn't specify an event. Please try again using /addevent.")
        return

    user_data[user_id].append({'date': str(datetime.date.today()), 'event': event_text})
    save_data(user_data)
    bot.reply_to(message, "Event recorded successfully!")

# Command to show all events of the user
@bot.message_handler(commands=['myevents'])
def show_events(message):
    user_id = str(message.from_user.id)
    events = user_data.get(user_id, [])

    if not events:
        bot.reply_to(message, "You have no recorded events.")
    else:
        response = "\n".join([f"{idx+1}: {event['date']}: {event['event']}" for idx, event in enumerate(events)])
        bot.reply_to(message, response)

# Command to delete an event
@bot.message_handler(commands=['deleteevent'])
def delete_event_prompt(message):
    list_and_prompt_for_action(message, "Select an event to delete by number:", process_event_deletion)

# Function to process the event deletion
def process_event_deletion(message):
    user_id = str(message.from_user.id)
    try:
        event_number = int(message.text) - 1
        if 0 <= event_number < len(user_data[user_id]):
            del user_data[user_id][event_number]
            save_data(user_data)
            bot.reply_to(message, "Event deleted successfully.")
        else:
            bot.reply_to(message, "Invalid event number.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid number.")

# Command to update an event
@bot.message_handler(commands=['updateevent'])
def update_event_prompt(message):
    list_and_prompt_for_action(message, "Select an event to update by number:", process_event_update)

# Function to process the event update
def process_event_update(message):
    user_id = str(message.from_user.id)
    try:
        parts = message.text.split(": ", 1)
        if len(parts) != 2:
            bot.reply_to(message, "Please enter a valid format: number: new details")
            return

        event_number, new_details = parts
        event_number = int(event_number) - 1  # Adjusting for 0-based indexing

        if not new_details:
            bot.reply_to(message, "Event details cannot be empty. Please try again.")
            return

        if 0 <= event_number < len(user_data[user_id]):
            user_data[user_id][event_number]['event'] = new_details
            save_data(user_data)
            bot.reply_to(message, "Event updated successfully.")
        else:
            bot.reply_to(message, "Invalid event number.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid format: number: new details")

# Helper function to list events and prompt for an action
def list_and_prompt_for_action(message, prompt, next_step_handler):
    user_id = str(message.from_user.id)
    events = user_data.get(user_id, [])
    if not events:
        bot.reply_to(message, "You have no recorded events.")
        return

    response = prompt + "\n" + "\n".join([f"{idx+1}: {event['date']}: {event['event']}" for idx, event in enumerate(events)])
    bot.send_message(message.chat.id, response)
    bot.register_next_step_handler(message, next_step_handler)

# Generic message handler for any other text
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.reply_to(message, "I didn't understand that. Use /start to see available commands.")

# Start the bot
bot.polling()
