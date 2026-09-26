# Expense Currency Assistant

A terminal assistant that reads expense data, calculates totals,
and converts currencies using an exchange-rate API.

## Features

- Streaming AI responses.
- Three tools: calculator, CSV reader, and exchange-rate lookup.
- Pydantic input validation.
- Network timeouts and limited retries.
- A maximum of eight tool executions per user request.
- Tool failures returned as readable error messages.

## How it works

```text
User question
    ↓
AI requests a tool
    ↓
Python validates the input and runs the tool
    ↓
Tool result returns to the AI
    ↓
AI answers or requests another tool
```

The AI chooses the tools. Python executes them.

## Tools

| Tool | Purpose |
|---|---|
| calculator | Calculate arithmetic expressions |
| read_data | Read a CSV from the data folder |
| get_fx_rate | Fetch the latest available daily exchange rate |

The CSV reader accepts files up to 100 KB and 50 data rows.

The calculator supports numbers, parentheses, addition,
subtraction, multiplication, and division.
Decimal calculations use 28 digits of precision.

Exchange rates come from Frankfurter.
They are reference data, not guaranteed bank transaction rates.

## Requirements

- Python 3.10 or newer.
- Internet access for AI responses and exchange rates.
- API credentials and a model endpoint compatible with
  Anthropic Messages, streaming, and tool use.

Access depends on the selected provider and account.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a local `.env` using `.env.example` as a reference.
Fill in your API key, base URL, and model.

Never commit `.env`.

## Run

```bash
python chat.py
```

Example request:

```text
Baca expenses.csv, jumlahkan pengeluarannya,
lalu konversikan total dari IDR ke USD.
Sebutkan tanggal kursnya.
```

The included sample CSV totals 525,000 IDR.
The USD result depends on the returned exchange rate.

Type `reset` to start a new conversation.
Type `exit` to close the application.

## Tests

```bash
python -m unittest discover -s tests -v
```

The automated tests use simulated API responses.
They do not require AI credentials or internet access.

Also check the real assistant manually for:

- A request using all three tools.
- A missing file.
- A failed exchange-rate lookup.
- Invalid arguments and model correction when observed.
- The tool-call limit.

