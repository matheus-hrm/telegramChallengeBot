# Telegram Banking Bot

A Telegram bot that allows users to manage their bank account by depositing, withdrawing, and checking their balance. The bot uses MongoDB to store user data and transactions.

## Features

- **Deposit**: Users can deposit money into their account.
- **Withdraw**: Users can withdraw money from their account.
- **Check Balance**: Users can check their current account balance.
- **Transaction History**: The bot maintains a history of all transactions.

## Requirements

- Python 3.10+
- MongoDB
- Telegram Bot API Token

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/matheus-hrm/telegramChallengeBot.git
    cd telegramChallengBot
    ```

2. **Create a virtual environment and activate it**:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up your environment variables following the `.env.example` file**:

    ```sh
    BOT_TOKEN='YOUR_TELEGRAM_BOT_TOKEN'
    MONGODB_URI='YOUR_MONGODB_URI'
    DB_NAME='YOUR_DATABASE_NAME'
    ```

## Usage

1. **Run the bot**:
    ```sh
    python3 main.py
    ```

2. **Interact with the bot**:
    - Start the bot by sending `/start` command.
    - Use the inline buttons to deposit, withdraw, or check your balance.

## Project Structure

```
telegram-banking-bot/
│
├── main.py                 # Main bot logic
├── db.py                   # Database interaction logic
├── callback.py             # Callback types for inline buttons
├── config.py               # Configuration file
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Example Commands

- **/start**: Initializes the bot and shows the main menu.
- **/deposit**: Prompts the user to enter the amount to deposit.
- **/withdraw**: Prompts the user to enter the amount to withdraw.
- **/balance**: Shows the user's current balance and last transaction.

## Error Handling

The bot includes error handling to manage unexpected issues. Errors are logged to the console.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram bot API wrapper.
- [MongoDB](https://www.mongodb.com/) for the database solution.

---
