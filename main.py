from callback import CallbackTypes
from config import token
from db import deposit, get_last_transaction, get_user_balance, withdraw
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [
        [
            InlineKeyboardButton("Deposit", callback_data=CallbackTypes.DEPOSIT.value),
            InlineKeyboardButton("Withdraw", callback_data=CallbackTypes.WITHDRAW.value),
            InlineKeyboardButton("Balance", callback_data=CallbackTypes.BALANCE.value),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Hello, use the three options to deposit, withdraw or check balance"
        ,reply_markup=reply_markup
    )

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Enter the amount you want to withdraw")
    context.user_data["action"] = CallbackTypes.WITHDRAW 
    
async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Enter the amount you want to deposit")
    context.user_data["action"] = CallbackTypes.DEPOSIT

# Callbacks
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith(CallbackTypes.DEPOSIT.value):
        await query.edit_message_text("Enter the amount you want to deposit")
        context.user_data["action"] = CallbackTypes.DEPOSIT

    elif data.startswith(CallbackTypes.WITHDRAW.value):
        await query.edit_message_text("Enter the amount you want to withdraw")
        context.user_data["action"] = CallbackTypes.WITHDRAW
       
    elif data.startswith(CallbackTypes.BALANCE.value):
        await handle_check_balance(update, context)
        context.user_data["action"] = CallbackTypes.BALANCE 
        
    elif data.startswith(CallbackTypes.CONFIRM_DEPOSIT.value):
        amount = context.user_data.get("deposit")
        await handle_deposit(amount, update, context)
    
    elif data.startswith(CallbackTypes.CONFIRM_WITHDRAW.value):
        amount = context.user_data.get("withdraw")
        await handle_withdraw(amount, update, context)

    elif data.startswith(CallbackTypes.CANCEL.value):
        await query.edit_message_text("Cancelled the action")
        context.user_data.pop("action")
        context.user_data.pop("deposit")
        context.user_data.pop("withdraw")
    else:
        await query.edit_message_text(f"Callback data: {data}")

async def handle_deposit(amount: int, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    deposited = await deposit(user_id, amount)
    replying = update.callback_query 
    if replying:
        if deposited:
            await update.callback_query.edit_message_text(f"Deposited {amount} successfully")
        else:
            await update.callback_query.edit_message_text(f"Failed to deposit {amount}")
    else:
        if deposited:
            await update.message.reply_text(f"Deposited {amount} successfully")
        else:
            await update.message.reply_text(f"Failed to deposit {amount}, Insufficient funds")
    context.user_data.pop("deposit")
    
async def handle_withdraw(amount: int, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    withdrew = await withdraw(user_id, amount)
    replying = update.callback_query
    if replying: # Reply if there is context or the user called a command
        if withdrew:
            await update.callback_query.edit_message_text(f"Withdrew {amount} successfully")
        else:
            await update.callback_query.edit_message_text(f"Failed to withdraw {amount}")
    else:
        if withdrew:
            await update.message.reply_text(f"Withdrew {amount} successfully")
        else:
            await update.message.reply_text(f"Failed to withdraw {amount}, Insufficient funds")
    context.user_data.pop("withdraw")

async def handle_check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    balance = await get_user_balance(user_id)
    last_transaction = await get_last_transaction(user_id)
    transaction = {
        "type": last_transaction.get("type"),
        "amount": last_transaction.get("amount"),
        "createdAt": last_transaction.get("createdAt").strftime("%Y-%m-%d %H:%M:%S")
    }
    if last_transaction:
        message = f"Your last transaction was a {transaction['type']} of ${transaction['amount']} on {transaction['createdAt']}"
    else: 
        message = "No transactions found"
    replying = update.callback_query
    if replying:
        await update.callback_query.edit_message_text(f"Your balance is ${balance}\n{message}")
    else:
        await update.message.reply_text(f"Your balance is ${balance}\n{message}")

# Response handler 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    
    text = update.message.text

    if context.user_data.get("action") == CallbackTypes.DEPOSIT:
        try:
            amount = int(text)
            
            if not isinstance(amount, int):                 
                raise ValueError("Amount must be an integer")
            if amount < 0:
                raise ValueError("Amount must be greater than 0")
            buttons = [[
                InlineKeyboardButton("Confirm", callback_data="confirm_deposit"),
                InlineKeyboardButton("Cancel", callback_data="cancel_deposit"),
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(
                f"Confirm deposit of {amount}?", reply_markup=reply_markup
            )
            context.user_data["deposit"] = amount
            context.user_data.pop("action")
        except ValueError:
            msg = "Invalid amount, please enter a valid amount"
            await update.message.reply_text(msg)
            return

    elif context.user_data.get("action") == CallbackTypes.WITHDRAW:
        try:
            amount = int(text)
            if amount < 0:
                raise ValueError("Amount must be greater than 0")
            buttons = [[
                InlineKeyboardButton("Confirm", callback_data="confirm_withdraw"),
                InlineKeyboardButton("Cancel", callback_data="cancel_withdraw"),
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text(
                f"Confirm withdraw of {amount}?", reply_markup=reply_markup
            )
            context.user_data["withdraw"] = amount
            context.user_data.pop("action")
        except ValueError:
            msg = "Invalid amount, please enter a valid amount"
            await update.message.reply_text(msg)
            return

    return text

# Error handler

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("An error occurred")
    print(f"An error occurred: {context.error} caused by {update}")

if __name__ == "__main__":
    print("Bot is starting")
    app = Application.builder().token(token).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", handle_check_balance))
    app.add_handler(CommandHandler("deposit", deposit_command))
    app.add_handler(CommandHandler("withdraw", withdraw_command))

    # Callbacks
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error handler
    app.add_error_handler(error)

    print("Bot is running")
    app.run_polling(poll_interval=3)
