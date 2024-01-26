# Smile Summary Bot

## Overview
This bot, aptly named the 'Smile Summary', is a Telegram bot designed to help users focus on the positive aspects of their lives by recording and recalling moments that made them smile.

It allows users to add, view, update, and delete their recorded smiles. The bot also prompts users weekly to share their happy moments.

## Features
- **Record Smiles:** Users can record their happy moments along with the date.
- **View Smiles:** Users can view all their recorded smiles.
- **Update Smiles:** Users can update the details of their recorded smiles.
- **Delete Smiles:** Users can delete any of their recorded smiles.
- **Weekly Prompts:** The bot sends weekly reminders to users to record their smiles.

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package installer)
- SQLite3

### Setup
#### Clone the Repository:
    git clone [repository-url]
    cd [repository-directory]

#### Create and Activate a Virtual Environment (Optional):
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

#### Install Dependencies:
    pip install -r requirements.txt

#### Set up the Telegram Bot Token:
- Create a bot in Telegram using BotFather and get the bot token.
- Set the bot token in `config.py`.

#### Initialize the Database:
- Ensure the SQLite database file path in `main.py` is correct.
- Run `main.py` to initialize the database.


## Usage

### Start the Bot:
    python main.py

### Interact with the Bot on Telegram:
- Use the command `/start` to initiate the bot.
- Follow the inline keyboard or command prompts to interact with the bot.

### Commands
- `/start`: Starts the bot and registers the user.
- `/addsmile`: Adds a new smile.
- `/mysmiles`: Displays all recorded smiles.
- `/updatesmile`: Updates a specific smile.
- `/deletesmile`: Deletes a specific smile.

## Development
- **Configurations:** Modify `settings.py` for bot token and other settings.
- **Logging:** Logs are saved in `bot.log`. Configure logging in `main.py`.

