import os
import tempfile
import unittest

from cleaner import clean_rows, dedupe, load_rows, normalize_headers, write_rows


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

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "data.csv")
            write_rows(path, [["name", "score"], ["ada", "10"]])
            self.assertEqual(load_rows(path), [["name", "score"], ["ada", "10"]])


if __name__ == "__main__":
    unittest.main()
