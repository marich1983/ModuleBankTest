import uuid

from fastapi import FastAPI, Header, HTTPException

app = FastAPI()


payments = {}


@app.post("/payments")
async def create_payment(
    body: dict,
    idempotency_key: str = Header(...),
    x_correlation_id: str = Header(...),
):
    print("=== PROVIDER REQUEST ===")
    print("body:", body)
    print("Idempotency-Key:", idempotency_key)
    print("X-Correlation-ID:", x_correlation_id)

    if idempotency_key in payments:
        print("DUPLICATE request")
        return {
            "providerPaymentId": payments[idempotency_key],
            "status": "ACCEPTED",
        }

    provider_payment_id = str(uuid.uuid4())

    payments[idempotency_key] = provider_payment_id

    return {
        "providerPaymentId": provider_payment_id,
        "status": "ACCEPTED",
    }
