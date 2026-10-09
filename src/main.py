from pathlib import Path

from io_utils import (
    ScheduleLoadError,
    display_schedule,
    get_class_input,
    load_schedule_from_file,
    print_menu,
    save_schedule_to_file,
)
from planner_logic import add_class, search_lessons


SCHEDULE_PATH = Path(__file__).absolute().parent.parent / "data" / "schedule.json"


def main() -> None:
    try:
        schedule = load_schedule_from_file(SCHEDULE_PATH)
    except ScheduleLoadError as error:
        print("Unable to load schedule: {}".format(error))
        return

    while True:
        choice = print_menu()

        if choice == "1":
            day, time, subject = get_class_input()
            old_length = len(schedule)
            schedule = add_class(schedule, day, time, subject)

            if len(schedule) > old_length:
                save_schedule_to_file(SCHEDULE_PATH, schedule)
                print("Lesson added and saved.")
            else:
                print("Lesson was not added; the subject may be empty.")

        elif choice == "2":
            display_schedule(schedule)

        elif choice == "3":
            query = input("Enter a subject to search for: ")
            results = search_lessons(schedule, query)
            if results:
                print("\nMatching lessons:")
                display_schedule(results)
            else:
                print("No lessons found.")

        elif choice == "4":
            print("Exiting the planner.")
            break

        else:
            print("Invalid option. Choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
