import json
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE_DIR = Path(__file__).absolute().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIR))

from io_utils import (
    ScheduleLoadError,
    load_schedule_from_file,
    save_schedule_to_file,
)


class TestScheduleFileIO(unittest.TestCase):
    def schedule_path(self, directory):
        return Path(directory) / "data" / "schedule.json"

    def write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def test_missing_schedule_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_schedule_from_file(self.schedule_path(directory)), [])

    def test_save_and_load_round_trip(self):
        schedule = [
            {"day": "Monday", "time": "09:00", "subject": "Physics"},
            {"day": "Tuesday", "time": "11:30", "subject": "History"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            save_schedule_to_file(path, schedule)
            self.assertEqual(load_schedule_from_file(path), schedule)

    def test_subject_with_old_delimiter_is_preserved(self):
        schedule = [
            {"day": "Monday", "time": "09:00", "subject": "Math | Physics"}
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            save_schedule_to_file(path, schedule)
            self.assertEqual(load_schedule_from_file(path), schedule)

    def test_unicode_is_preserved(self):
        schedule = [
            {
                "day": "Понеділок",
                "time": "08:30",
                "subject": "Програмування — українською",
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            save_schedule_to_file(path, schedule)
            self.assertIn("Програмування", path.read_text(encoding="utf-8"))
            self.assertEqual(load_schedule_from_file(path), schedule)

    def test_malformed_json_raises_load_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            path.parent.mkdir(parents=True)
            path.write_text("{broken", encoding="utf-8")
            with self.assertRaises(ScheduleLoadError):
                load_schedule_from_file(path)

    def test_non_array_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            self.write_json(path, {"lessons": []})
            with self.assertRaises(ScheduleLoadError):
                load_schedule_from_file(path)

    def test_non_object_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.schedule_path(directory)
            self.write_json(path, [None])
            with self.assertRaises(ScheduleLoadError):
                load_schedule_from_file(path)

    def test_missing_required_field_is_rejected(self):
        for missing_field in ("day", "time", "subject"):
            with self.subTest(field=missing_field):
                entry = {"day": "Monday", "time": "09:00", "subject": "Math"}
                del entry[missing_field]
                with tempfile.TemporaryDirectory() as directory:
                    path = self.schedule_path(directory)
                    self.write_json(path, [entry])
                    with self.assertRaises(ScheduleLoadError):
                        load_schedule_from_file(path)

    def test_non_string_required_field_is_rejected(self):
        for field in ("day", "time", "subject"):
            with self.subTest(field=field):
                entry = {"day": "Monday", "time": "09:00", "subject": "Math"}
                entry[field] = 42
                with tempfile.TemporaryDirectory() as directory:
                    path = self.schedule_path(directory)
                    self.write_json(path, [entry])
                    with self.assertRaises(ScheduleLoadError):
                        load_schedule_from_file(path)


if __name__ == "__main__":
    unittest.main()
