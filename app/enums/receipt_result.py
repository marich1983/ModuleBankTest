from enum import Enum


class ReceiptResult(str, Enum):
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
