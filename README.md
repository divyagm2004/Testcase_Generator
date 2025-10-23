# Testcases Generator Bot

This is a Streamlit-based web application that uses AI models to generate test cases from user stories. It supports history tracking, downloading, and deletion of generated test cases.

This README provides quick setup and usage instructions, outlines the project structure, and gives notes for development and testing.

## Features

- Generate test cases using **OpenAI** or **Gemini** models.
- View and manage **history** of generated test cases.
- Download test cases as `.txt` files.
- Delete individual or all test cases from history.

## Requirements

- Python 3.10+ (project was tested on Python 3.11/3.12)
- pip

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

If you use a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Quick start

The repository contains an entrypoint `run.py`. To run the app locally:

```bash
# from project root
python run.py
```

By default the project uses the SQLite file `test.db` located in the repo root. If you need a clean database, delete `test.db` and let the app recreate it.

## Project layout

Top-level files:

- `run.py` — application entrypoint
- `requirements.txt` — Python dependencies
- `test.db` — local SQLite database (development)
- `README.md` — this file

app/ (package)

- `models/` — database connection and storage models
	- `database.py` — DB connection and helpers
	- `storage.py` — functions to persist and retrieve testcases
- `routes/` — HTTP (or CLI) entry routes
	- `app.py` — main route definitions
- `services/` — core business logic
	- `testcase_agent.py` — orchestration for testcase creation

## How it works (high level)

- `run.py` boots the application and wires together routes and services.
- The `testcase_agent` service contains the generation logic and uses `storage` to persist results.
- `database.py` provides a small wrapper around SQLite connections used by storage.

## Development tips

- Run the app directly with `python run.py` while developing.
- Use the existing `test.db` file for persistence; back it up before destructive testing.
