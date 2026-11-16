import os
import tempfile
import unittest

from cleaner import clean_rows, dedupe, drop_empty_columns, load_rows, normalize_headers, select_columns, write_rows


class CleanerTests(unittest.TestCase):
    def test_clean_rows_trims_and_drops_blank_rows(self):
        rows = [[" a ", " b "], [" ", ""], ["c", "d"]]
        self.assertEqual(clean_rows(rows), [["a", "b"], ["c", "d"]])

    def test_normalize_headers(self):
        self.assertEqual(
            normalize_headers([" First Name ", "Total Spend", "!!!"]),
            ["first_name", "total_spend", "column"],
        )

    def test_dedupe_preserves_first_occurrence_order(self):
        rows = [["a", "1"], ["b", "2"], ["a", "1"]]
        self.assertEqual(dedupe(rows), [["a", "1"], ["b", "2"]])

    def test_dedupe_by_key(self):
        rows = [["a", "1"], ["a", "2"], ["b", "3"]]
        self.assertEqual(dedupe(rows, key=0), [["a", "1"], ["b", "3"]])

    def test_drop_empty_columns(self):
        rows = [["name", "", "score"], ["ada", "", "10"], ["grace", "", "9"]]
        self.assertEqual(
            drop_empty_columns(rows),
            [["name", "score"], ["ada", "10"], ["grace", "9"]],
        )

    def test_drop_empty_columns_empty_input(self):
        self.assertEqual(drop_empty_columns([]), [])

    def test_select_columns_reorders(self):
        rows = [["name", "score", "city"], ["ada", "10", "London"]]
        self.assertEqual(
            select_columns(rows, ["city", "name"]),
            [["city", "name"], ["London", "ada"]],
        )

    def test_select_columns_missing_raises(self):
        rows = [["name", "score"], ["ada", "10"]]
        with self.assertRaises(ValueError):
            select_columns(rows, ["name", "age"])

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "data.csv")
            write_rows(path, [["name", "score"], ["ada", "10"]])
            self.assertEqual(load_rows(path), [["name", "score"], ["ada", "10"]])


class CleanFileTests(unittest.TestCase):
    def test_clean_file_reports_and_writes(self):
        from cleaner import clean_file

        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "raw.csv")
            destination = os.path.join(directory, "clean.csv")
            write_rows(
                source,
                [
                    [" Name ", " Score "],
                    ["ada", "10"],
                    ["ada", "10"],
                    [" ", " "],
                    ["grace", "9"],
                ],
            )
            stats = clean_file(source, destination)
            self.assertEqual(stats["headers"], ["name", "score"])
            self.assertEqual(stats["rows_after"], 2)
            self.assertEqual(stats["duplicates_removed"], 1)
            self.assertEqual(
                load_rows(destination),
                [["name", "score"], ["ada", "10"], ["grace", "9"]],
            )


class DelimiterTests(unittest.TestCase):
    def test_roundtrip_with_semicolon(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "data.csv")
            write_rows(path, [["name", "score"], ["ada", "10"]], delimiter=";")
            self.assertEqual(
                load_rows(path, delimiter=";"),
                [["name", "score"], ["ada", "10"]],
            )

    def test_clean_file_semicolon_input_and_output(self):
        from cleaner import clean_file

        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "raw.csv")
            destination = os.path.join(directory, "clean.csv")
            write_rows(
                source,
                [
                    [" Name ", " Score "],
                    ["ada", "10"],
                    ["ada", "10"],
                    [" ", " "],
                    ["grace", "9"],
                ],
                delimiter=";",
            )
            stats = clean_file(source, destination, delimiter=";")
            self.assertEqual(stats["headers"], ["name", "score"])
            self.assertEqual(stats["rows_before"], 4)
            self.assertEqual(stats["rows_after"], 2)
            self.assertEqual(stats["duplicates_removed"], 1)
            self.assertEqual(
                load_rows(destination, delimiter=";"),
                [["name", "score"], ["ada", "10"], ["grace", "9"]],
            )

    def test_clean_file_reads_semicolon_and_writes_comma(self):
        from cleaner import clean_file

        with tempfile.TemporaryDirectory() as directory:
            source = os.path.join(directory, "raw.csv")
            destination = os.path.join(directory, "clean.csv")
            write_rows(
                source,
                [["Name", "Score"], ["ada", "10"], ["ada", "10"]],
                delimiter=";",
            )
            stats = clean_file(
                source, destination, delimiter=";", out_delimiter=","
            )
            self.assertEqual(stats["duplicates_removed"], 1)
            self.assertEqual(
                load_rows(destination),
                [["name", "score"], ["ada", "10"]],
            )


if __name__ == "__main__":
    unittest.main()
