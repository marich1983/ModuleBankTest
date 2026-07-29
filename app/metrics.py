from prometheus_client import Counter, Gauge

OPERATIONS_TOTAL = Counter(
    "operations_total",
    "Total created operations"
)

PROVIDER_REQUESTS_TOTAL = Counter(
    "provider_requests_total",
    "Requests sent to provider"
)

PROVIDER_RETRIES_TOTAL = Counter(
    "provider_retries_total",
    "Provider retries"
)

PROVIDER_ERRORS_TOTAL = Counter(
    "provider_errors_total",
    "Provider errors"
)

RECEIPT_RECEIVED_TOTAL = Counter(
    "receipt_received_total",
    "Received receipts"
)

OPERATIONS_PENDING = Gauge(
    "operations_processing_total",
    "Operations waiting for provider result",
)

