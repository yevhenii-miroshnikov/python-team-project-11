from datetime import datetime


WEEKDAY_ALIASES = {
    "monday": "Monday",
    "mon": "Monday",
    "пн": "Monday",
    "понеділок": "Monday",
    "tuesday": "Tuesday",
    "tue": "Tuesday",
    "вт": "Tuesday",
    "вівторок": "Tuesday",
    "wednesday": "Wednesday",
    "wed": "Wednesday",
    "ср": "Wednesday",
    "середа": "Wednesday",
    "thursday": "Thursday",
    "thu": "Thursday",
    "чт": "Thursday",
    "четвер": "Thursday",
    "friday": "Friday",
    "fri": "Friday",
    "пт": "Friday",
    "п'ятниця": "Friday",
    "пʼятниця": "Friday",
    "пятниця": "Friday",
    "saturday": "Saturday",
    "sat": "Saturday",
    "сб": "Saturday",
    "субота": "Saturday",
    "sunday": "Sunday",
    "sun": "Sunday",
    "нд": "Sunday",
    "неділя": "Sunday",
}
WEEKDAY_ORDER = {
    weekday: index
    for index, weekday in enumerate(
        (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )
    )
}


def _input_text(value, field_name):
    """Convert API input to trimmed text while rejecting None explicitly."""
    if value is None:
        raise ValueError("{} must not be None.".format(field_name))
    return str(value).strip()


def normalize_weekday(value):
    """Return the English canonical weekday for a supported alias."""
    weekday = _input_text(value, "Weekday").casefold()
    try:
        return WEEKDAY_ALIASES[weekday]
    except KeyError as error:
        raise ValueError("Unknown weekday: {!r}.".format(value)) from error


def normalize_time(value):
    """Return a valid 24-hour time in canonical HH:MM form."""
    time_value = _input_text(value, "Time").replace(".", ":")
    try:
        parsed_time = datetime.strptime(time_value, "%H:%M")
    except ValueError as error:
        raise ValueError(
            "Invalid time {!r}; expected a time between 00:00 and 23:59.".format(
                value
            )
        ) from error
    return "{:02d}:{:02d}".format(parsed_time.hour, parsed_time.minute)


def create_lesson(day, time, subject):
    """Validate lesson fields and return a normalized lesson dictionary."""
    normalized_day = normalize_weekday(day)
    normalized_time = normalize_time(time)
    normalized_subject = _input_text(subject, "Subject")
    if not normalized_subject:
        raise ValueError("Subject must not be empty.")

    return {
        "day": normalized_day,
        "time": normalized_time,
        "subject": normalized_subject,
    }


def add_class(schedule, day, time, subject):
    """Append a validated lesson unless that weekday and time are occupied."""
    new_lesson = create_lesson(day, time, subject)
    for lesson in schedule:
        existing_day = normalize_weekday(lesson["day"])
        existing_time = normalize_time(lesson["time"])
        if (
            existing_day == new_lesson["day"]
            and existing_time == new_lesson["time"]
        ):
            raise ValueError(
                "A lesson already exists on {} at {}.".format(
                    new_lesson["day"], new_lesson["time"]
                )
            )

    schedule.append(new_lesson)
    return schedule


def sort_schedule(schedule):
    """Return lessons sorted by weekday and time without mutating the input."""
    return sorted(
        schedule,
        key=lambda lesson: (
            WEEKDAY_ORDER[normalize_weekday(lesson["day"])],
            normalize_time(lesson["time"]),
        ),
    )


def search_lessons(schedule, query):
    """Return lessons whose subject contains a non-empty query, ignoring case."""
    search_query = query.strip().casefold()
    if not search_query:
        return []
    return [
        lesson
        for lesson in schedule
        if search_query in lesson["subject"].casefold()
    ]
