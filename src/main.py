from pathlib import Path

from io_utils import (
    ScheduleLoadError,
    display_schedule,
    get_class_input,
    load_schedule_from_file,
    print_menu,
    save_schedule_to_file,
)
from planner_logic import add_class, search_lessons, sort_schedule


SCHEDULE_PATH = Path(__file__).absolute().parent.parent / "data" / "schedule.json"


def validate_schedule(schedule):
    """Raise ValueError if lessons are invalid or conflict with each other."""
    validated_schedule = []
    for lesson in schedule:
        add_class(
            validated_schedule,
            lesson["day"],
            lesson["time"],
            lesson["subject"],
        )


def main(schedule_path=None) -> None:
    if schedule_path is None:
        schedule_path = SCHEDULE_PATH

    try:
        schedule = load_schedule_from_file(schedule_path)
    except ScheduleLoadError as error:
        print("Unable to load schedule: {}".format(error))
        return

    try:
        validate_schedule(schedule)
    except ValueError as error:
        print("Schedule contains invalid lesson data: {}".format(error))
        return

    while True:
        choice = print_menu()

        if choice == "1":
            day, time, subject = get_class_input()
            try:
                schedule = add_class(schedule, day, time, subject)
            except ValueError as error:
                print("Error: {}".format(error))
                continue

            save_schedule_to_file(schedule_path, schedule)
            print("Lesson added and saved.")

        elif choice == "2":
            display_schedule(sort_schedule(schedule))

        elif choice == "3":
            query = input("Enter a subject to search for: ")
            results = search_lessons(schedule, query)
            if results:
                print("\nMatching lessons:")
                display_schedule(sort_schedule(results))
            else:
                print("No lessons found.")

        elif choice == "4":
            print("Exiting the planner.")
            break

        else:
            print("Invalid option. Choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
