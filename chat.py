from typing import Any

from anthropic import (
    Anthropic,
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
)

from assistant import run_turn
from config import (
    API_KEY,
    BASE_URL,
    MODEL,
    get_max_tool_calls,
    validate_config,
)


def main() -> None:
    try:
        validate_config()
        max_tool_calls = get_max_tool_calls()

    except ValueError as exc:
        print(f"Pengaturan belum siap: {exc}")
        return

    history: list[dict[str, Any]] = []

    print("Expense Currency Assistant")
    print("Ketik pertanyaanmu.")
    print("Ketik 'reset' untuk percakapan baru.")
    print("Ketik 'exit' untuk keluar.")

    with Anthropic(
        api_key=API_KEY,
        base_url=BASE_URL,
        timeout=10.0,
        max_retries=2,
    ) as client:
        while True:
            try:
                user_text = input("\nKamu: ").strip()

            except (KeyboardInterrupt, EOFError):
                print("\nSampai nanti!")
                break

            if user_text.lower() in {"exit", "quit"}:
                print("Sampai nanti!")
                break

            if user_text.lower() == "reset":
                history.clear()
                print("Percakapan sudah direset.")
                continue

            if not user_text:
                continue

            try:
                run_turn(
                    client=client,
                    model=MODEL,
                    history=history,
                    user_text=user_text,
                    max_tool_calls=max_tool_calls,
                )

            except APITimeoutError:
                print(
                    "\nKoneksi AI terlalu lama. "
                    "Pertanyaan ini belum disimpan; coba lagi."
                )

            except APIConnectionError:
                print(
                    "\nTidak bisa terhubung ke AI. "
                    "Periksa internet dan alamat API."
                )

            except APIStatusError as exc:
                print(
                    f"\nAPI AI mengembalikan status {exc.status_code}. "
                    "Periksa API key, akses model, dan kuota akun."
                )

            except KeyboardInterrupt:
                print("\nProses dibatalkan. Kamu bisa bertanya lagi.")

            except Exception as exc:
                print(
                    "\nProses belum berhasil. "
                    f"Jenis kesalahan: {type(exc).__name__}. "
                    "Periksa konfigurasi dan dukungan endpoint."
                )


if __name__ == "__main__":
    main()