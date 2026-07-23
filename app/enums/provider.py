from enum import Enum

class PaymentProvider(str, Enum):
    PROVIDER_SIMULATOR = "PROVIDER_SIMULATOR"
    TINKOFF = "TINKOFF"
    SBER = "SBER"