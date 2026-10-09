import json
from pathlib import Path
from typing import Dict, List, Union


REQUIRED_FIELDS = ("day", "time", "subject")


class ScheduleLoadError(Exception):
    """Raised when a schedule file cannot be read or validated."""


def load_schedule_from_file(filepath: Union[str, Path]) -> List[Dict[str, str]]:
    """Load and validate a JSON schedule; a missing file means no lessons yet."""
    path = Path(filepath)
    try:
        with path.open("r", encoding="utf-8") as schedule_file:
            schedule = json.load(schedule_file)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ScheduleLoadError(
            "The schedule file is not valid UTF-8 JSON: {}".format(error)
        ) from error
    except OSError as error:
        raise ScheduleLoadError(
            "The schedule file could not be read: {}".format(error)
        ) from error

    if not isinstance(schedule, list):
        raise ScheduleLoadError("The schedule JSON root must be an array.")

    for index, lesson in enumerate(schedule, start=1):
        if not isinstance(lesson, dict):
            raise ScheduleLoadError(
                "Schedule entry {} must be a JSON object.".format(index)
            )
        for field in REQUIRED_FIELDS:
            if field not in lesson:
                raise ScheduleLoadError(
                    "Schedule entry {} is missing the '{}' field.".format(
                        index, field
                    )
                )
            if not isinstance(lesson[field], str):
                raise ScheduleLoadError(
                    "The '{}' field in schedule entry {} must be a string.".format(
                        field, index
                    )
                )

    return schedule


def save_schedule_to_file(
    filepath: Union[str, Path], schedule: List[Dict[str, str]]
) -> None:
    """Save the complete schedule as readable UTF-8 JSON."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as schedule_file:
        json.dump(schedule, schedule_file, ensure_ascii=False, indent=2)
        schedule_file.write("\n")


def print_menu() -> str:
    """Display the main menu and return the selected option."""
    print("\n--- Weekly Study Planner ---")
    print("1. Add a lesson")
    print("2. View the schedule")
    print("3. Search by subject")
    print("4. Exit")
    return input("Choose an option: ")


def get_class_input() -> tuple:
    """Prompt for lesson details; weekday names remain Ukrainian for now."""
    day = input("Day of week (enter a Ukrainian name or abbreviation): ")
    time = input("Time (e.g. 08:30): ")
    subject = input("Subject: ")
    return day, time, subject


def format_lesson(lesson: Dict[str, str]) -> str:
    """Format one lesson for display."""
    return "[{}] {} - {}".format(lesson["day"], lesson["time"], lesson["subject"])


def display_schedule(schedule: List[Dict[str, str]]) -> None:
    """Print all lessons, or an empty-schedule message."""
    if not schedule:
        print("The schedule is empty.")
        return
    for lesson in schedule:
        print(format_lesson(lesson))
