import json
import unittest
from unittest.mock import patch

import httpx

from tools import calculator, execute_tool, files, fx


class ToolTests(unittest.TestCase):
    def test_calculator_percentage(self) -> None:
        result = calculator.run(
            {"expression": "12.5 / 100 * 3840"}
        )
        self.assertEqual(float(result), 480.0)

    def test_calculator_decimal(self) -> None:
        result = calculator.run({"expression": "0.1 + 0.2"})
        self.assertEqual(result, "0.3")

    def test_calculator_zero_division(self) -> None:
        result = calculator.run({"expression": "10 / 0"})
        self.assertTrue(result.startswith("ERROR:"))

    def test_calculator_wrong_input_type(self) -> None:
        result = calculator.run({"expression": 123})
        self.assertTrue(result.startswith("ERROR:"))

    def test_calculator_rejects_function_call(self) -> None:
        result = calculator.run({"expression": "sum([1, 2])"})
        self.assertTrue(result.startswith("ERROR:"))

    def test_read_expenses(self) -> None:
        result = files.run({"filename": "expenses.csv"})
        data = json.loads(result)
        self.assertEqual(len(data["rows"]), 3)

    def test_missing_file(self) -> None:
        result = files.run({"filename": "missing.csv"})
        self.assertTrue(result.startswith("ERROR:"))

    def test_file_outside_data_folder(self) -> None:
        result = files.run({"filename": "../.env"})
        self.assertTrue(result.startswith("ERROR:"))

    def test_unknown_tool(self) -> None:
        result = execute_tool("unknown_tool", {})
        self.assertTrue(result.startswith("ERROR:"))

    def test_invalid_currency_code(self) -> None:
        result = fx.run({"base": "RUPIAH", "quote": "USD"})
        self.assertTrue(result.startswith("ERROR:"))

    @patch("tools.fx.time.sleep")
    @patch("tools.fx.httpx.get")
    def test_fx_retries_network_failure(
        self,
        mock_get,
        mock_sleep,
    ) -> None:
        request = httpx.Request(
            "GET",
            "https://api.frankfurter.dev/v2/rate/idr/usd",
        )

        response = httpx.Response(
            200,
            request=request,
            json={
                "base": "IDR",
                "quote": "USD",
                "rate": 0.00006,
                "date": "2026-01-02",
            },
        )

        mock_get.side_effect = [
            httpx.ConnectError("Simulated offline"),
            response,
        ]

        result = fx.run({"base": "IDR", "quote": "USD"})
        data = json.loads(result)

        self.assertEqual(data["rate"], 0.00006)
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    @patch("tools.fx.time.sleep")
    @patch("tools.fx.httpx.get")
    def test_fx_stops_after_three_failures(
        self,
        mock_get,
        mock_sleep,
    ) -> None:
        mock_get.side_effect = httpx.ConnectError(
            "Simulated offline"
        )

        result = fx.run({"base": "IDR", "quote": "USD"})

        self.assertTrue(result.startswith("ERROR:"))
        self.assertEqual(mock_get.call_count, 3)


if __name__ == "__main__":
    unittest.main()