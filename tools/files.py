import csv
import json
from itertools import islice
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR = DATA_DIR.resolve()

MAX_FILE_BYTES = 100_000
MAX_ROWS = 50


class ReadDataInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    filename: str = Field(min_length=1, max_length=100)


def run(args: dict[str, Any]) -> str:
    try:
        validated = ReadDataInput.model_validate(args)
        path = (DATA_DIR / validated.filename).resolve()

        if not path.is_relative_to(DATA_DIR):
            return "ERROR: hanya boleh membaca file di folder data."

        if path.suffix.lower() != ".csv":
            return "ERROR: hanya file CSV yang didukung."

        if not path.is_file():
            return "ERROR: file tidak ditemukan."

        if path.stat().st_size > MAX_FILE_BYTES:
            return "ERROR: ukuran file melebihi 100 KB."

        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            columns = reader.fieldnames
            rows = list(islice(reader, MAX_ROWS + 1))

        if not columns or not rows:
            return "ERROR: CSV kosong atau tidak memiliki data."

        if len(rows) > MAX_ROWS:
            return "ERROR: CSV melebihi 50 baris. Gunakan file lebih kecil."

        return json.dumps(
            {
                "filename": validated.filename,
                "columns": columns,
                "rows": rows,
            },
            ensure_ascii=False,
        )

    except Exception as exc:
        return f"ERROR: gagal membaca CSV: {exc}"