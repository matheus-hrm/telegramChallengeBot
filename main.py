from callback import CallbackTypes
from config import token
from db import add_payment_method, deposit, get_last_transaction, get_payment_methods, get_user_balance, withdraw
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
        amount = context.user_data.get("deposit_amount")
        if amount:
            await handle_deposit(amount, update, context)
            context.user_data.pop("deposit_amount", None)
            context.user_data.pop("method_type", None)
        else:
            await query.edit_message_text("No deposit amount found")
    
    elif data.startswith(CallbackTypes.CONFIRM_WITHDRAW.value):
        amount = context.user_data.get("withdraw_amount")
        await handle_withdraw(amount, update, context)
    
    elif data.startswith(CallbackTypes.ADD_METHOD.value):
        await handle_add_method(update, context)

    elif data.startswith(CallbackTypes.METHOD_TYPE.value):
        await handle_method_type_selection(update, context)
    
    elif data.startswith(CallbackTypes.CRYPTO_TYPE.value):
        crypto = data.replace(CallbackTypes.CRYPTO_TYPE.value, "")
        context.user_data["crypto_currency"] = crypto.upper()
        await query.edit_message_text(f"Enter your {crypto.upper()} address:")
    
    elif data.startswith(CallbackTypes.SELECT_METHOD.value):
        method_type = data.replace(CallbackTypes.SELECT_METHOD.value, "")
        if context.user_data.get("deposit_amount"):
            amount = context.user_data["deposit_amount"]
            buttons = [[
                InlineKeyboardButton("Confirm", callback_data=f"{CallbackTypes.CONFIRM_DEPOSIT.value}"),
                InlineKeyboardButton("Cancel", callback_data=CallbackTypes.CANCEL.value),
            ]]
            await query.edit_message_text(
                f"Confirm deposit of {amount} using {method_type}?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        elif context.user_data.get("withdraw_amount"):
            amount = context.user_data["withdraw_amount"]
            buttons = [[
                InlineKeyboardButton("Confirm", callback_data=CallbackTypes.CONFIRM_WITHDRAW.value),
                InlineKeyboardButton("Cancel", callback_data=CallbackTypes.CANCEL.value),
            ]]
            await query.edit_message_text(
                f"Confirm withdraw of {amount} using {method_type}?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )


    elif data.startswith(CallbackTypes.CANCEL.value):
        await query.edit_message_text("Cancelled the action")
        context.user_data.pop("action")
        context.user_data.pop("deposit_amount")
        context.user_data.pop("withdraw_amount")
    else:
        await query.edit_message_text("Unknown command")

async def handle_deposit(amount: int, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    deposited = await deposit(user_id, amount)

    replying = update.callback_query 
    if replying:
        if deposited:
            await update.callback_query.edit_message_text(f"Deposited {amount} successfully")
        else:
            await update.callback_query.edit_message_text(f"Failed to deposit {amount}, Insufficient funds")
    else:
        if deposited:
            await update.message.reply_text(f"Deposited {amount} successfully")
        else:
            await update.message.reply_text(f"Failed to deposit {amount}, Insufficient funds")

    context.user_data.pop("deposit_amount", None)
    context.user_data.pop("method_type", None)
    context.user_data.pop("action", None)
    
async def handle_withdraw(amount: int, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    withdrew = await withdraw(user_id, amount)
    replying = update.callback_query
    if replying: 
        if withdrew:
            await update.callback_query.edit_message_text(f"Withdrew {amount} successfully")
        else:
            await update.callback_query.edit_message_text(f"Failed to withdraw {amount}, Insufficient funds")
    else:
        if withdrew:
            await update.message.reply_text(f"Withdrew {amount} successfully")
        else:
            await update.message.reply_text(f"Failed to withdraw {amount}, Insufficient funds")

    context.user_data.pop("withdraw_amount", None)
    context.user_data.pop("method_type", None)
    context.user_data.pop("action", None)

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

async def handle_add_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [
        [
            InlineKeyboardButton("Bank Transfer", callback_data=f"{CallbackTypes.METHOD_TYPE.value}bank"),
            InlineKeyboardButton("PayPal", callback_data=f"{CallbackTypes.METHOD_TYPE.value}paypal"),
            InlineKeyboardButton("Crypto", callback_data=f"{CallbackTypes.METHOD_TYPE.value}crypto"),
        ],
        [InlineKeyboardButton("Cancel", callback_data=CallbackTypes.CANCEL.value)]
    ]
    await update.callback_query.edit_message_text(
        "Select payment method type:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    context.user_data["adding_method"] = True

async def handle_method_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    method_type = query.data.replace(CallbackTypes.METHOD_TYPE.value, "")

    context.user_data["adding_method"] = True
    context.user_data["method_type"] = method_type

    if method_type == "bank":
        await query.edit_message_text("Enter your bank name:")
    elif method_type == "paypal":
        await query.edit_message_text("Enter your PayPal email:")
    elif method_type == "crypto":
        buttons = [
            [
                InlineKeyboardButton("BTC", callback_data=f"{CallbackTypes.CRYPTO_TYPE.value}btc"),
                InlineKeyboardButton("ETH", callback_data=f"{CallbackTypes.CRYPTO_TYPE.value}eth"),
                InlineKeyboardButton("USDT", callback_data=f"{CallbackTypes.CRYPTO_TYPE.value}usdt"),
            ],
            [InlineKeyboardButton("Cancel", callback_data=CallbackTypes.CANCEL.value)]
        ]
        await query.edit_message_text(
            "Select cryptocurrency:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
async def show_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    methods = await get_payment_methods(user_id)
    print(methods)
    
    buttons = []
    for method in methods:
        label = format_method_label(method)
        buttons.append([InlineKeyboardButton(
            label, 
            callback_data=f"{CallbackTypes.SELECT_METHOD.value}{method['type']}"
        )])
    
    buttons.append([
        InlineKeyboardButton("Add New Method", callback_data=CallbackTypes.ADD_METHOD.value),
        InlineKeyboardButton("Cancel", callback_data=CallbackTypes.CANCEL.value)
    ])
    
    await update.message.reply_text(
        "Select payment method:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def format_method_label(method: dict) -> str:
    try:
        method_type = method.get("type")
        data = method.get("data", {})
        
        match method_type:
            case "bank":
                return f"Bank Transfer: {data.get('bank_name', 'Unknown Bank')}"
            case "paypal":
                return f"PayPal: {data.get('email', 'No Email')}"
            case "crypto":
                currency = data.get('currency', 'Unknown')
                return f"Crypto: {currency}"
            case _:
                return f"Unknown Method: {method_type}"
    except Exception as e:
        print(f"Error formatting method label: {e}")
        return "Invalid Method"

# Response handler 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    
    text = update.message.text
    user_id = update.effective_user.id

    if context.user_data.get("method_type"):
        method_type = context.user_data.get("method_type")
        match method_type:
            case "bank":
                await add_payment_method(user_id, "bank", {"bank_name": text})
            case "paypal":
                await add_payment_method(user_id, "paypal", {"email": text})
            case "crypto":
                await add_payment_method(user_id, "crypto", {
                    "currency": context.user_data.get("crypto_currency"),
                    "address": text
                })
        
        context.user_data.pop("method_type")
    
        if context.user_data.get("deposit_amount"):
            amount = context.user_data["deposit_amount"]
            buttons = [[
                InlineKeyboardButton("Confirm", callback_data=CallbackTypes.CONFIRM_DEPOSIT.value),
                InlineKeyboardButton("Cancel", callback_data=CallbackTypes.CANCEL.value),
            ]]
            await update.message.reply_text(
                f"Confirm deposit of {amount}?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        if context.user_data.get("withdraw_amount"):
            amount = context.user_data["withdraw_amount"]
            buttons = [[
                InlineKeyboardButton("Confirm", callback_data=CallbackTypes.CONFIRM_WITHDRAW.value),
                InlineKeyboardButton("Cancel", callback_data=CallbackTypes.CANCEL.value),
            ]]
            await update.callback_query.edit_message_text(
                f"Confirm withdraw of {amount}?",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await handle_withdraw(amount, update, context)
        return

    if context.user_data.get("action") == CallbackTypes.DEPOSIT:
        try:
            amount = int(text)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            context.user_data["deposit_amount"] = amount
            await show_method_selection(update, context)
            return
        except ValueError:
            await update.message.reply_text("Invalid amount, please enter a valid amount")
            return

    elif context.user_data.get("action") == CallbackTypes.WITHDRAW:
        try:
            amount = int(text)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            context.user_data["withdraw_amount"] = amount
            await show_method_selection(update, context)
            return
        except ValueError:
            await update.message.reply_text("Invalid amount, please enter a valid amount")
            return

# Error handler

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text("An error occurred")
        elif update and update.message:
            await update.message.reply_text("An error occurred")
    except Exception as e:
        print(f"Error in error handler: {e}")
    print(f"Update {update} caused error {context.error}")

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
