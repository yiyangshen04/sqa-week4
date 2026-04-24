# Week 4 — To-Do List Backend

A testable, dependency-injected to-do list domain model in Python, with a pytest unit-test suite demonstrating AAA structure, the four pillars of a good unit test, and multiple test-double styles (mock, stub, fake, spy, dummy).

## Requirements

- Python 3.10+
- `pytest` and `pytest-cov`

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run tests

```bash
pytest
```

## Regenerate coverage report

```bash
pytest --cov=src --cov-branch --cov-report=term-missing --cov-report=html
open htmlcov/index.html
```

## Project layout

```
src/
  models/        — Task, User, Priority enum
  repositories/  — in-memory task & user storage behind protocols
  services/      — AuthService, TaskService, password hasher, reminder service
  exceptions.py  — named exception hierarchy (no bare Exception)
  clock.py       — Clock protocol + SystemClock + FixedClock (deterministic test clock)
tests/           — pytest unit tests, AAA-structured
```
