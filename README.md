# Weekly Study Planner

A small modular Python CLI application for managing a weekly study schedule, originally developed as a two-person university project and later independently refined for portfolio use by Yevhenii Miroshnikov.

## Project Context

The project was created for a university Python programming course. The two-person assignment focused on modular development, console interaction, file persistence, and unit testing. After the coursework, Yevhenii independently refined the project for portfolio use, improving validation, persistence safety, and automated tests.

## 📖 Table of Contents

- [Team Contributions](#team-contributions)
- [Portfolio Refinement](#portfolio-refinement)
- [Implemented Features](#implemented-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Run Locally](#run-locally)
- [Verification](#verification)
- [Data Storage](#data-storage)
- [Scope and Limitations](#scope-and-limitations)
- [Kurzbeschreibung](#german)
- [Contact](#contact)

## Team Contributions

- **Yevhenii Miroshnikov — original contribution:** project structure, console interface and I/O, original text-file persistence, and module integration in `main.py`.
- **Veronika Tormozova — original contribution:** planner business logic, weekday normalization and search, and the original unit tests.

The later portfolio refinement was completed independently by Yevhenii after the original coursework. The original contributions remain attributed to both authors.

## Portfolio Refinement

For the portfolio version, Yevhenii migrated the original delimiter-based text storage to JSON, added safe loading with structural and semantic validation, and made schedule paths project-relative. Planner updates introduced canonical English weekdays with legacy Ukrainian aliases, strict time validation, subject case preservation, duplicate-timeslot detection, chronological sorting, and removal of broad exception handling. The work also expanded planner, persistence, and CLI integration tests, added the English CLI, and updated the documentation. The refactor deliberately kept the project dependency-free and preserved its simple modular structure instead of introducing heavier abstractions for a small CLI application.

## Implemented Features

- Add and view lessons containing a weekday, time, and subject.
- Search subjects using a case-insensitive substring query.
- Normalize supported weekday names and aliases to English weekday names.
- Validate 24-hour times and reject occupied weekday/time slots.
- Display lessons in weekday and time order.
- Store the schedule in JSON and reject malformed or semantically invalid stored data without silently replacing it.

## Technology Stack

- Python 3 (verified with Python 3.9.13)
- Python Standard Library, including `datetime`, `json`, and `pathlib`
- `unittest` for automated tests
- Git and GitHub

The application has no third-party runtime dependencies.

## Project Structure

```text
python-team-project-11/
├── data/
│   └── schedule.json       # Local schedule data
├── src/
│   ├── main.py             # CLI flow and application integration
│   ├── io_utils.py         # Prompts, display, and JSON persistence
│   └── planner_logic.py    # Validation, conflicts, sorting, and search
├── tests/
│   ├── test_main.py        # CLI integration tests
│   ├── test_io_utils.py    # JSON persistence tests
│   └── test_planner.py     # Planner logic tests
└── README.md
```

## Run Locally

From the repository root in Windows PowerShell:

```powershell
git clone https://github.com/yevhenii-miroshnikov/python-team-project-11.git
cd python-team-project-11
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python src\main.py
```

No package installation step is required.

## Verification

Run the test suite from the repository root:

```powershell
python -m unittest discover -s tests -v
```

The tests cover planner input validation and normalization, conflicts, sorting and search, JSON persistence and malformed data handling, and CLI integration. The full suite currently contains 41 tests.

## Data Storage

The schedule is stored as human-readable UTF-8 JSON in `data/schedule.json`:

```json
[
  {
    "day": "Monday",
    "time": "08:30",
    "subject": "Programming"
  }
]
```

JSON replaced the original delimiter-based text format to keep fields structured, avoid delimiter ambiguity, and allow validation before data is used. Invalid stored data is reported and left unchanged.

## Scope and Limitations

This is a small local academic CLI project. It has no graphical interface, multi-user support, database or backend, or lesson edit/delete workflow. Schedule data remains in a local JSON file; the project makes no production or security claims.

<a id="german"></a>

## 🇩🇪 Kurzbeschreibung

Dieses kleine Python-Studienprojekt entstand ursprünglich in einem Zweier-Team und wurde später von Yevhenii Miroshnikov unabhängig für sein Portfolio technisch weiterentwickelt. Die CLI-Anwendung verwaltet einen wöchentlichen Lernplan mit validierten Wochentagen und Uhrzeiten, Konfliktprüfung, chronologischer Sortierung und lokaler JSON-Speicherung.

<a id="contact"></a>

## 📬 Contact

- **GitHub:** [@yevhenii-miroshnikov](https://github.com/yevhenii-miroshnikov)
- **LinkedIn:** [yevhenii-miroshnikov](https://www.linkedin.com/in/yevhenii-miroshnikov)
