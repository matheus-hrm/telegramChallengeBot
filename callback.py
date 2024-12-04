from enum import Enum

class CallbackTypes(Enum):
    DEPOSIT = "deposit_"
    WITHDRAW = "withdraw_"
    BALANCE = "balance_"
    CONFIRM_WITHDRAW = "confirm_withdraw"
    CONFIRM_DEPOSIT = "confirm_deposit"
    CANCEL = "cancel_"
    ADD_METHOD = "add_method_"
    SELECT_METHOD = "select_method_"
    METHOD_TYPE = "method_type_"
    CRYPTO_TYPE = "crypto_type_" 