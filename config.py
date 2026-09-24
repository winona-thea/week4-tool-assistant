import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "").strip()
MODEL = os.getenv("ANTHROPIC_MODEL", "").strip()


def get_max_tool_calls() -> int:
    value = int(os.getenv("MAX_TOOL_CALLS", "8"))

    if not 1 <= value <= 8:
        raise ValueError("MAX_TOOL_CALLS harus antara 1 dan 8.")

    return value


def validate_config() -> None:
    if not API_KEY:
        raise ValueError("Isi ANTHROPIC_API_KEY di file .env.")

    if API_KEY in {
        "replace_with_your_api_key",
        "isi_api_key_aslimu_di_sini",
    }:
        raise ValueError("Ganti contoh API key dengan API key milikmu.")

    if not BASE_URL:
        raise ValueError("Isi ANTHROPIC_BASE_URL di file .env.")

    if not MODEL:
        raise ValueError("Isi ANTHROPIC_MODEL di file .env.")