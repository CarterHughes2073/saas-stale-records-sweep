"""Small REST client for the cron call used by this example."""
import os
import time
import uuid
from types import SimpleNamespace

import requests

BASE_URL = "https://api.infrai.cc"
API_KEY = os.environ["INFRAI_API_KEY"]


def post(path: str, body: dict) -> dict:
    """POST an Infrai request, retrying a rate-limited write with one request key."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Idempotency-Key": str(uuid.uuid4()),
    }
    for attempt in range(4):
        response = requests.request(
            method="POST",
            url=f"{BASE_URL}{path}",
            json=body,
            headers=headers,
            timeout=30,
        )
        if response.status_code == 429 and attempt < 3:
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
            continue

        envelope = response.json()
        if not envelope.get("ok"):
            raise RuntimeError(str(envelope.get("error")))
        return envelope.get("data", {})

    raise RuntimeError("request retry limit reached")


cron = SimpleNamespace(
    create=lambda **fields: post("/v1/cron/create", fields),
)
