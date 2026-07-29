import logging


class ContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "operation_id"):
            record.operation_id = "-"
        if not hasattr(record, "provider_payment_id"):
            record.provider_payment_id = "-"
        if not hasattr(record, "attempt"):
            record.attempt = "-"
        return True

def setup_logging() -> None:
    print("LOGGING SETUP CALLED")
    handler = logging.StreamHandler()

    handler.addFilter(ContextFilter())

    formatter = logging.Formatter(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s "
            "%(message)s "
            "operation_id=%(operation_id)s "
            "provider_payment_id=%(provider_payment_id)s "
            "attempt=%(attempt)s"
    )

    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


