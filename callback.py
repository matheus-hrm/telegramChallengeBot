from enum import Enum

class CallbackTypes(Enum):
    DEPOSIT = "deposit_"
    WITHDRAW = "withdraw_"
    BALANCE = "balance_"
    CONFIRM_WITHDRAW = "confirm_withdraw"
    CONFIRM_DEPOSIT = "confirm_deposit"
    CANCEL = "cancel_"