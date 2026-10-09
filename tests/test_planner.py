import sys
import unittest
from pathlib import Path


SOURCE_DIR = Path(__file__).absolute().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIR))

from planner_logic import (
    add_class,
    create_lesson,
    normalize_time,
    normalize_weekday,
    search_lessons,
    sort_schedule,
)


class TestWeekdayNormalization(unittest.TestCase):
    def test_english_full_names(self):
        weekdays = (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )
        for weekday in weekdays:
            with self.subTest(weekday=weekday):
                self.assertEqual(normalize_weekday(weekday), weekday)

    def test_english_abbreviations(self):
        cases = (
            ("Mon", "Monday"),
            ("Tue", "Tuesday"),
            ("Wed", "Wednesday"),
            ("Thu", "Thursday"),
            ("Fri", "Friday"),
            ("Sat", "Saturday"),
            ("Sun", "Sunday"),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(normalize_weekday(value), expected)

    def test_case_and_surrounding_whitespace(self):
        self.assertEqual(normalize_weekday(" mon "), "Monday")
        self.assertEqual(normalize_weekday("MONDAY"), "Monday")

    def test_ukrainian_legacy_aliases(self):
        cases = (
            ("пн", "Monday"),
            ("понеділок", "Monday"),
            ("вт", "Tuesday"),
            ("вівторок", "Tuesday"),
            ("ср", "Wednesday"),
            ("середа", "Wednesday"),
            ("чт", "Thursday"),
            ("четвер", "Thursday"),
            ("пт", "Friday"),
            ("п'ятниця", "Friday"),
            ("пʼятниця", "Friday"),
            ("пятниця", "Friday"),
            ("сб", "Saturday"),
            ("субота", "Saturday"),
            ("нд", "Sunday"),
            ("неділя", "Sunday"),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(normalize_weekday(value), expected)

    def test_unknown_weekday_is_rejected(self):
        for value in ("Mondayyyy", "abc"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_weekday(value)

    def test_empty_weekday_is_rejected(self):
        for value in ("", "   "):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_weekday(value)


class TestTimeNormalization(unittest.TestCase):
    def test_supported_formats_return_canonical_time(self):
        for value in ("08:30", "8:30", "08.30", "8.30"):
            with self.subTest(value=value):
                self.assertEqual(normalize_time(value), "08:30")
        self.assertEqual(normalize_time("8:03"), "08:03")
        self.assertEqual(normalize_time("00:00"), "00:00")
        self.assertEqual(normalize_time("23:59"), "23:59")

    def test_invalid_time_is_rejected(self):
        for value in ("24:00", "12:60", "12:75", "abc", "", "   "):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_time(value)


class TestLessonCreation(unittest.TestCase):
    def test_valid_lesson_is_normalized(self):
        self.assertEqual(
            create_lesson(" mon ", "8.30", "  SQL  "),
            {"day": "Monday", "time": "08:30", "subject": "SQL"},
        )

    def test_subject_case_is_preserved(self):
        for subject in ("SQL", "REST API", "C++"):
            with self.subTest(subject=subject):
                lesson = create_lesson("Monday", "08:30", subject)
                self.assertEqual(lesson["subject"], subject)

    def test_empty_subject_is_rejected(self):
        for subject in ("", "   "):
            with self.subTest(subject=subject):
                with self.assertRaises(ValueError):
                    create_lesson("Monday", "08:30", subject)

    def test_invalid_fields_are_rejected(self):
        invalid_lessons = (
            ("Mondayyyy", "08:30", "Math"),
            ("Monday", "24:00", "Math"),
            ("Monday", "08:30", "   "),
        )
        for lesson_fields in invalid_lessons:
            with self.subTest(lesson_fields=lesson_fields):
                with self.assertRaises(ValueError):
                    create_lesson(*lesson_fields)

    def test_none_values_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Weekday"):
            normalize_weekday(None)
        with self.assertRaisesRegex(ValueError, "Time"):
            normalize_time(None)
        with self.assertRaisesRegex(ValueError, "Subject"):
            create_lesson("Monday", "08:30", None)


class TestAddingLessons(unittest.TestCase):
    def test_valid_lesson_is_added(self):
        schedule = []
        result = add_class(schedule, "Tuesday", "10:00", "Physics")
        self.assertIs(result, schedule)
        self.assertEqual(
            schedule,
            [{"day": "Tuesday", "time": "10:00", "subject": "Physics"}],
        )

    def test_same_canonical_day_and_time_conflict_is_rejected(self):
        schedule = [
            {"day": "пн", "time": "8.30", "subject": "Mathematics"}
        ]
        with self.assertRaisesRegex(ValueError, "already exists"):
            add_class(schedule, "Monday", "08:30", "Physics")
        self.assertEqual(len(schedule), 1)
        self.assertEqual(schedule[0]["subject"], "Mathematics")

    def test_invalid_existing_entry_is_rejected_without_append(self):
        invalid_entries = (
            {"day": "Funday", "time": "08:30", "subject": "Unknown day"},
            {"day": "Tuesday", "time": "24:00", "subject": "Invalid time"},
        )
        for entry in invalid_entries:
            with self.subTest(entry=entry):
                schedule = [entry]
                with self.assertRaises(ValueError):
                    add_class(schedule, "Monday", "09:00", "Physics")
                self.assertEqual(schedule, [entry])

    def test_different_time_or_day_is_allowed(self):
        schedule = [{"day": "Monday", "time": "08:30", "subject": "Math"}]
        add_class(schedule, "Monday", "10:00", "Physics")
        add_class(schedule, "Tuesday", "08:30", "History")
        self.assertEqual(len(schedule), 3)

    def test_invalid_input_is_not_appended(self):
        invalid_lessons = (
            ("not a weekday", "08:30", "Math"),
            ("Monday", "12:60", "Math"),
            ("Monday", "08:30", "   "),
        )
        for lesson_fields in invalid_lessons:
            with self.subTest(lesson_fields=lesson_fields):
                schedule = []
                with self.assertRaises(ValueError):
                    add_class(schedule, *lesson_fields)
                self.assertEqual(schedule, [])


class TestLessonSearch(unittest.TestCase):
    def setUp(self):
        self.schedule = [
            {"day": "Monday", "time": "08:30", "subject": "REST API Design"},
            {"day": "Tuesday", "time": "10:00", "subject": "Mathematics"},
        ]

    def test_case_insensitive_substring_search(self):
        self.assertEqual(search_lessons(self.schedule, "rest api"), [self.schedule[0]])

    def test_no_match_returns_empty_list(self):
        self.assertEqual(search_lessons(self.schedule, "biology"), [])

    def test_empty_query_returns_empty_list(self):
        for query in ("", "   "):
            with self.subTest(query=query):
                self.assertEqual(search_lessons(self.schedule, query), [])


class TestScheduleSorting(unittest.TestCase):
    def test_weekdays_sort_from_monday_to_sunday(self):
        weekdays = (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        )
        schedule = [
            {"day": weekday, "time": "09:00", "subject": weekday}
            for weekday in reversed(weekdays)
        ]
        sorted_schedule = sort_schedule(schedule)
        self.assertEqual(
            [lesson["day"] for lesson in sorted_schedule], list(weekdays)
        )

    def test_mixed_schedule_sorts_by_day_then_time_without_mutation(self):
        schedule = [
            {"day": "Friday", "time": "11:00", "subject": "Friday"},
            {"day": "Понеділок", "time": "14:00", "subject": "Monday late"},
            {"day": "Tuesday", "time": "09:00", "subject": "Tuesday"},
            {"day": "Monday", "time": "8.30", "subject": "Monday early"},
        ]
        original_schedule = list(schedule)

        sorted_schedule = sort_schedule(schedule)

        self.assertEqual(
            [lesson["subject"] for lesson in sorted_schedule],
            ["Monday early", "Monday late", "Tuesday", "Friday"],
        )
        self.assertEqual(schedule, original_schedule)
        self.assertEqual(schedule[0]["subject"], "Friday")


if __name__ == "__main__":
    unittest.main()
