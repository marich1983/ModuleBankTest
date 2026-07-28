from enum import Enum


class OperationProvider(str, Enum):
    PROVIDER_SIMULATOR = "PROVIDER_SIMULATOR"
    TINKOFF = "TINKOFF"
    SBER = "SBER"
