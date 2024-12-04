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
    METHOD_TYPE_BANK = "method_type_bank"
    METHOD_TYPE_PAYPAL = "method_type_paypal"
    METHOD_TYPE_CRYPTO = "method_type_crypto"
    CRYPTO_TYPE = "crypto_type_"
    CRYPTO_TYPE_BTC = "crypto_type_btc"
    CRYPTO_TYPE_ETH = "crypto_type_eth"
    CRYPTO_TYPE_USDT = "crypto_type_usdt"

    

DEPOSIT = CallbackTypes.DEPOSIT.value
WITHDRAW = CallbackTypes.WITHDRAW.value
BALANCE = CallbackTypes.BALANCE.value
CONFIRM_WITHDRAW = CallbackTypes.CONFIRM_WITHDRAW.value
CONFIRM_DEPOSIT = CallbackTypes.CONFIRM_DEPOSIT.value
CANCEL = CallbackTypes.CANCEL.value
ADD_METHOD = CallbackTypes.ADD_METHOD.value
SELECT_METHOD = CallbackTypes.SELECT_METHOD.value
METHOD_TYPE = CallbackTypes.METHOD_TYPE.value
METHOD_TYPE_BANK = CallbackTypes.METHOD_TYPE_BANK.value
METHOD_TYPE_PAYPAL = CallbackTypes.METHOD_TYPE_PAYPAL.value
METHOD_TYPE_CRYPTO = CallbackTypes.METHOD_TYPE_CRYPTO.value
CRYPTO_TYPE = CallbackTypes.CRYPTO_TYPE.value
CRYPTO_TYPE_BTC = CallbackTypes.CRYPTO_TYPE_BTC.value
CRYPTO_TYPE_ETH = CallbackTypes.CRYPTO_TYPE_ETH.value
CRYPTO_TYPE_USDT = CallbackTypes.CRYPTO_TYPE_USDT.value
