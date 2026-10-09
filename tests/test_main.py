import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SOURCE_DIR = Path(__file__).absolute().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIR))

import main as planner_app
from io_utils import get_class_input, load_schedule_from_file, save_schedule_to_file


class TestPlannerCLI(unittest.TestCase):
    def schedule_path(self, directory):
        return Path(directory) / "data" / "schedule.json"

    def run_cli(self, schedule_path, responses):
        output = io.StringIO()
        with patch("builtins.input", side_effect=responses), redirect_stdout(output):
            planner_app.main(schedule_path)
        return output.getvalue()

    def test_successful_add_is_persisted_in_canonical_format(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            output = self.run_cli(path, ["1", "Mon", "8.30", "SQL", "4"])

            self.assertIn("Lesson added and saved.", output)
            self.assertEqual(
                load_schedule_from_file(path),
                [{"day": "Monday", "time": "08:30", "subject": "SQL"}],
            )

    def test_invalid_weekday_does_not_save_and_returns_to_menu(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            output = self.run_cli(
                path, ["1", "Funday", "08:30", "Physics", "4"]
            )

            self.assertIn("Error: Unknown weekday: 'Funday'.", output)
            self.assertIn("Exiting the planner.", output)
            self.assertFalse(path.exists())

    def test_invalid_time_does_not_save_and_returns_to_menu(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            output = self.run_cli(
                path, ["1", "Monday", "25:00", "Physics", "4"]
            )

            self.assertIn("Error: Invalid time '25:00'", output)
            self.assertIn("Exiting the planner.", output)
            self.assertFalse(path.exists())

    def test_empty_subject_does_not_save_and_returns_to_menu(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            output = self.run_cli(
                path, ["1", "Monday", "08:30", "   ", "4"]
            )

            self.assertIn("Error: Subject must not be empty.", output)
            self.assertIn("Exiting the planner.", output)
            self.assertFalse(path.exists())

    def test_conflict_does_not_save_or_change_existing_data(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            initial_schedule = [
                {"day": "Monday", "time": "08:30", "subject": "Mathematics"}
            ]
            save_schedule_to_file(path, initial_schedule)
            before = path.read_bytes()

            output = self.run_cli(
                path, ["1", "Mon", "8.30", "Physics", "4"]
            )

            self.assertIn(
                "Error: A lesson already exists on Monday at 08:30.", output
            )
            self.assertIn("Exiting the planner.", output)
            self.assertEqual(path.read_bytes(), before)

    def test_view_displays_lessons_in_chronological_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            save_schedule_to_file(
                path,
                [
                    {"day": "Friday", "time": "11:00", "subject": "Friday"},
                    {"day": "Monday", "time": "14:00", "subject": "Monday late"},
                    {"day": "Monday", "time": "08:30", "subject": "Monday early"},
                    {"day": "Tuesday", "time": "09:00", "subject": "Tuesday"},
                ],
            )
            displayed = []

            with patch.object(
                planner_app,
                "display_schedule",
                side_effect=lambda lessons: displayed.append(list(lessons)),
            ):
                self.run_cli(path, ["2", "4"])

            self.assertEqual(
                [lesson["subject"] for lesson in displayed[0]],
                ["Monday early", "Monday late", "Tuesday", "Friday"],
            )

    def test_search_results_are_displayed_chronologically(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            save_schedule_to_file(
                path,
                [
                    {
                        "day": "Friday",
                        "time": "11:00",
                        "subject": "Physics Friday",
                    },
                    {"day": "Tuesday", "time": "09:00", "subject": "PHYSICS lab"},
                    {"day": "Monday", "time": "14:00", "subject": "Physics late"},
                    {"day": "Monday", "time": "08:30", "subject": "Physics early"},
                    {"day": "Wednesday", "time": "10:00", "subject": "History"},
                ],
            )
            displayed = []

            with patch.object(
                planner_app,
                "display_schedule",
                side_effect=lambda lessons: displayed.append(list(lessons)),
            ):
                self.run_cli(path, ["3", "pHySiCs", "4"])

            self.assertEqual(
                [lesson["subject"] for lesson in displayed[0]],
                ["Physics early", "Physics late", "PHYSICS lab", "Physics Friday"],
            )

    def test_semantically_invalid_loaded_data_is_not_overwritten(self):
        invalid_schedules = (
            ([{"day": "Funday", "time": "08:30", "subject": "Example"}], "weekday"),
            ([{"day": "Monday", "time": "99:99", "subject": "Example"}], "time"),
            (
                [
                    {"day": "Monday", "time": "08:30", "subject": "First"},
                    {"day": "Mon", "time": "8.30", "subject": "Duplicate"},
                ],
                "already exists",
            ),
        )
        for schedule, expected_error in invalid_schedules:
            with self.subTest(expected_error=expected_error):
                with tempfile.TemporaryDirectory() as directory:
                    path = self.schedule_path(directory)
                    path.parent.mkdir(parents=True)
                    path.write_text(
                        json.dumps(schedule, ensure_ascii=False), encoding="utf-8"
                    )
                    before = path.read_bytes()
                    output = io.StringIO()

                    with patch("builtins.input") as input_mock:
                        with redirect_stdout(output):
                            planner_app.main(path)

                    input_mock.assert_not_called()
                    self.assertIn("Schedule contains invalid lesson data:", output.getvalue())
                    self.assertIn(expected_error, output.getvalue())
                    self.assertEqual(path.read_bytes(), before)

    def test_lesson_prompts_are_english(self):
        prompts = [
            "Day of week (e.g. Monday or Mon): ",
            "Time (e.g. 08:30): ",
            "Subject: ",
        ]
        with patch("builtins.input", side_effect=["Monday", "08:30", "SQL"]) as input_mock:
            self.assertEqual(get_class_input(), ("Monday", "08:30", "SQL"))

        self.assertEqual(
            [call.args[0] for call in input_mock.call_args_list], prompts
        )


if __name__ == "__main__":
    unittest.main()
