from enum import Enum

class PaymentStatus(str, Enum):
    CREATED = "CREATED"   # Операция создана, отправка ещё не запрошена
    PROCESSING = "PROCESSING"   # Намерение отправки надёжно сохранено, ожидается результат провайдера
    COMPLETED = "COMPLETED"	  # Провайдер подтвердил успех callback-квитанцией
    REJECTED = "REJECTED"  # Провайдер подтвердил отказ callback-квитанцией


