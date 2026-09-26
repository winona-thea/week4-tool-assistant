from typing import Any, Callable

from tools import calculator, files, fx


REGISTRY: dict[str, Callable[[dict[str, Any]], str]] = {
    "calculator": calculator.run,
    "read_data": files.run,
    "get_fx_rate": fx.run,
}


TOOLS: list[dict[str, Any]] = [
    {
        "name": "calculator",
        "description": (
            "Use for all arithmetic, including totals, percentages, "
            "and multiplying an amount by an exchange rate. "
            "Use numbers, parentheses, +, -, *, and /."
        ),
        "input_schema": calculator.CalcInput.model_json_schema(),
    },
    {
        "name": "read_data",
        "description": (
            "Use when the user asks about expenses stored in a CSV file. "
            "Read a CSV from the data folder using its filename, "
            "for example expenses.csv."
        ),
        "input_schema": files.ReadDataInput.model_json_schema(),
    },
    {
        "name": "get_fx_rate",
        "description": (
            "Use when converting between currencies. "
            "Return the latest available daily rate and its date. "
            "Multiply the amount in base currency by rate "
            "to obtain the amount in quote currency."
        ),
        "input_schema": fx.FxInput.model_json_schema(),
    },
]


def execute_tool(name: str, args: dict[str, Any]) -> str:
    function = REGISTRY.get(name)

    if function is None:
        return f"ERROR: tool '{name}' tidak tersedia."

    try:
        return function(args)

    except Exception:
        return "ERROR: tool mengalami kesalahan yang tidak terduga."