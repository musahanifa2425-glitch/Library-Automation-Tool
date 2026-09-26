"""
test_library.py
-----------------
Unit tests for the Library Automation Tool.

Run with:
    python -m unittest test_library.py -v

Tests run headless (no tkinter import) and use a temporary JSON file
so they never touch the real books_data.json used by the GUI.
"""

import os
import tempfile
import unittest

from book_manager import BookManager
from exceptions import LibraryOperationError, ValidationError
from validators import validate_book_id, validate_isbn, validate_name


class TestValidators(unittest.TestCase):
    def test_validate_name_accepts_valid_name(self):
        self.assertEqual(validate_name("Clean Code", "Title"), "Clean Code")

    def test_validate_name_rejects_empty(self):
        with self.assertRaises(ValidationError):
            validate_name("   ", "Title")

    def test_validate_name_rejects_invalid_characters(self):
        with self.assertRaises(ValidationError):
            validate_name("Bad@Title!!", "Title")

    def test_validate_isbn_accepts_isbn13_with_hyphens(self):
        self.assertEqual(validate_isbn("978-0-13-235088-4"), "9780132350884")

    def test_validate_isbn_accepts_isbn10_with_x(self):
        self.assertEqual(validate_isbn("043942089X"), "043942089X")

    def test_validate_isbn_rejects_bad_isbn(self):
        with self.assertRaises(ValidationError):
            validate_isbn("12345")

    def test_validate_book_id_rejects_non_numeric(self):
        with self.assertRaises(ValidationError):
            validate_book_id("abc", [1, 2, 3])

    def test_validate_book_id_rejects_unknown_id(self):
        with self.assertRaises(ValidationError):
            validate_book_id("99", [1, 2, 3])


class TestBookManager(unittest.TestCase):
    def setUp(self):
        fd, self.tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.tmp_path)  # start with no file -> empty catalog
        self.manager = BookManager(file_path=self.tmp_path)

    def tearDown(self):
        for path in (self.tmp_path, self.tmp_path + ".tmp"):
            if os.path.exists(path):
                os.remove(path)

    def test_add_book(self):
        book = self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        self.assertEqual(book["status"], "Available")
        self.assertEqual(len(self.manager.books), 1)

    def test_add_duplicate_isbn_fails(self):
        self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        with self.assertRaises(LibraryOperationError):
            self.manager.add_book("Dune (Reprint)", "Frank Herbert", "9780441013593")

    def test_remove_book(self):
        book = self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        self.manager.remove_book(book["id"])
        self.assertEqual(len(self.manager.books), 0)

    def test_cannot_remove_issued_book(self):
        book = self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        self.manager.issue_book(book["id"], "Rahul Verma")
        with self.assertRaises(LibraryOperationError):
            self.manager.remove_book(book["id"])

    def test_issue_and_return_book(self):
        book = self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        issued = self.manager.issue_book(book["id"], "Rahul Verma")
        self.assertEqual(issued["status"], "Issued")
        returned = self.manager.return_book(book["id"])
        self.assertEqual(returned["status"], "Available")
        self.assertIsNone(returned["issued_to"])

    def test_cannot_issue_already_issued_book(self):
        book = self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        self.manager.issue_book(book["id"], "Rahul Verma")
        with self.assertRaises(LibraryOperationError):
            self.manager.issue_book(book["id"], "Someone Else")

    def test_cannot_return_available_book(self):
        book = self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        with self.assertRaises(LibraryOperationError):
            self.manager.return_book(book["id"])

    def test_search_books(self):
        self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        self.manager.add_book("Foundation", "Isaac Asimov", "9780553293357")
        results = self.manager.search_books("dune")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Dune")

    def test_get_stats(self):
        b1 = self.manager.add_book("Dune", "Frank Herbert", "9780441013593")
        self.manager.add_book("Foundation", "Isaac Asimov", "9780553293357")
        self.manager.issue_book(b1["id"], "Rahul Verma")
        stats = self.manager.get_stats()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["issued"], 1)
        self.assertEqual(stats["available"], 1)


if __name__ == "__main__":
    unittest.main()
