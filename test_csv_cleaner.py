import os
import tempfile
import unittest

from cleaner import clean_rows, dedupe, drop_empty_columns, fill_missing, load_rows, normalize_headers, select_columns, sort_rows, write_rows


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

    def test_fill_missing_pads_ragged_rows(self):
        rows = [["a"], ["b", "c"], ["d", "e", "f"]]
        self.assertEqual(
            fill_missing(rows),
            [["a", "", ""], ["b", "c", ""], ["d", "e", "f"]],
        )

    def test_fill_missing_leaves_even_rows_unchanged(self):
        rows = [["a", "b"], ["c", "d"]]
        self.assertEqual(fill_missing(rows), rows)

    def test_fill_missing_empty_input(self):
        self.assertEqual(fill_missing([]), [])

    def test_fill_missing_custom_value(self):
        rows = [["a"], ["b", "c"]]
        self.assertEqual(fill_missing(rows, value="N/A"), [["a", "N/A"], ["b", "c"]])

    def test_fill_missing_does_not_truncate_long_rows(self):
        rows = [["a"], ["b", "c", "d"]]
        self.assertEqual(
            fill_missing(rows),
            [["a", "", ""], ["b", "c", "d"]],
        )

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


class SortRowsTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            ["name", "score"],
            ["grace", "9"],
            ["ada", "10"],
        ]

    def test_sorts_body_by_column(self):
        self.assertEqual(
            sort_rows(self.rows, "score"),
            [["name", "score"], ["ada", "10"], ["grace", "9"]],
        )

    def test_header_preserved(self):
        rows = [["name", "score"], ["grace", "9"], ["ada", "10"]]
        self.assertEqual(sort_rows(rows, "name")[0], ["name", "score"])

    def test_reverse(self):
        self.assertEqual(
            sort_rows(self.rows, "score", reverse=True),
            [["name", "score"], ["grace", "9"], ["ada", "10"]],
        )

    def test_missing_column_raises(self):
        with self.assertRaises(ValueError):
            sort_rows(self.rows, "age")

    def test_empty_rows(self):
        self.assertEqual(sort_rows([], "score"), [])


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


class RenameColumnsTests(unittest.TestCase):
    def test_renames_known_columns(self):
        from cleaner import rename_columns

        rows = [["name", "score"], ["ada", "10"]]
        self.assertEqual(
            rename_columns(rows, {"score": "points"}),
            [["name", "points"], ["ada", "10"]],
        )

    def test_unknown_columns_untouched(self):
        from cleaner import rename_columns

        self.assertEqual(rename_columns([["a", "b"]], {}), [["a", "b"]])

    def test_empty_rows(self):
        from cleaner import rename_columns

        self.assertEqual(rename_columns([], {"a": "b"}), [])


if __name__ == "__main__":
    unittest.main()
