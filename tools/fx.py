import json
import math
import time
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field


class FxInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    base: str = Field(pattern=r"^[A-Za-z]{3}$")
    quote: str = Field(pattern=r"^[A-Za-z]{3}$")


def fetch_rate(base: str, quote: str) -> dict[str, Any]:
    url = (
        "https://api.frankfurter.dev/v2/rate/"
        f"{base.lower()}/{quote.lower()}"
    )

    for attempt in range(3):
        try:
            response = httpx.get(url, timeout=8.0)

        except httpx.TransportError:
            if attempt == 2:
                raise

            time.sleep(2 ** attempt)
            continue

        if response.status_code == 429:
            # Ikuti waktu tunggu server jika tersedia.
            retry_after = response.headers.get("Retry-After")

            if retry_after is not None:
                try:
                    delay = float(retry_after)
                except ValueError:
                    raise ValueError(
                        "API sedang membatasi permintaan. Coba lagi nanti."
                    )
            else:
                delay = float(2 ** attempt)

            if attempt == 2 or not 0 <= delay <= 10:
                raise ValueError(
                    "API sedang membatasi permintaan. Coba lagi nanti."
                )

            time.sleep(delay)
            continue

        if 500 <= response.status_code < 600 and attempt < 2:
            time.sleep(2 ** attempt)
            continue

        response.raise_for_status()
        payload = response.json()

        if not isinstance(payload, dict):
            raise ValueError("Bentuk jawaban API tidak sesuai.")

        rate = float(payload["rate"])

        if not math.isfinite(rate) or rate <= 0:
            raise ValueError("Nilai kurs tidak valid.")

        if (
            str(payload.get("base", "")).upper() != base
            or str(payload.get("quote", "")).upper() != quote
        ):
            raise ValueError("Pasangan mata uang dari API tidak sesuai.")

        return {
            "base": base,
            "quote": quote,
            "rate": rate,
            "date": payload["date"],
            "source": "Frankfurter",
        }

    raise ValueError("Kurs belum berhasil diambil.")


def run(args: dict[str, Any]) -> str:
    try:
        validated = FxInput.model_validate(args)
        base = validated.base.upper()
        quote = validated.quote.upper()

        if base == quote:
            return json.dumps(
                {
                    "base": base,
                    "quote": quote,
                    "rate": 1,
                    "date": None,
                    "source": "Mata uang sama",
                }
            )

        return json.dumps(fetch_rate(base, quote))

    except Exception as exc:
        return f"ERROR: gagal mengambil kurs: {exc}"