"""
book_manager.py
----------------
Core business logic for the Library Automation Tool.

BookManager owns the in-memory catalog and every operation on it
(add, remove, search, issue, return). It delegates persistence to
data_handler and input validation to validators, and turns the raw
catalog into useful views such as search results and statistics
("data processing").
"""

from datetime import date

from data_handler import DEFAULT_DATA_FILE, load_books, save_books
from exceptions import LibraryOperationError
from validators import validate_book_id, validate_isbn, validate_name


class BookManager:
    def __init__(self, file_path: str = DEFAULT_DATA_FILE):
        self.file_path = file_path
        self.books = load_books(file_path)
        self._next_id = self._compute_next_id()

    def _compute_next_id(self) -> int:
        if not self.books:
            return 1
        return max(book["id"] for book in self.books) + 1

    def _save(self) -> None:
        save_books(self.books, self.file_path)

    # ---------------------------------------------------------- Add
    def add_book(self, title: str, author: str, isbn: str) -> dict:
        title = validate_name(title, "Title")
        author = validate_name(author, "Author")
        isbn = validate_isbn(isbn)

        if any(b["isbn"] == isbn for b in self.books):
            raise LibraryOperationError(f"A book with ISBN {isbn} already exists.")

        book = {
            "id": self._next_id,
            "title": title,
            "author": author,
            "isbn": isbn,
            "status": "Available",
            "issued_to": None,
            "issue_date": None,
        }
        self.books.append(book)
        self._next_id += 1
        self._save()
        return book

    # ------------------------------------------------------- Remove
    def remove_book(self, book_id) -> dict:
        book_id = validate_book_id(book_id, [b["id"] for b in self.books])
        book = next(b for b in self.books if b["id"] == book_id)
        if book["status"] == "Issued":
            raise LibraryOperationError(
                "Cannot remove a book that is currently issued. Return it first."
            )
        self.books.remove(book)
        self._save()
        return book

    # ---------------------------------------------- Search (processing)
    def search_books(self, keyword: str) -> list:
        keyword = (keyword or "").strip().lower()
        if not keyword:
            return list(self.books)
        return [
            b for b in self.books
            if keyword in b["title"].lower()
            or keyword in b["author"].lower()
            or keyword in b["isbn"].lower()
        ]

    # -------------------------------------------------------- Issue
    def issue_book(self, book_id, member_name: str) -> dict:
        book_id = validate_book_id(book_id, [b["id"] for b in self.books])
        member_name = validate_name(member_name, "Member name")

        book = next(b for b in self.books if b["id"] == book_id)
        if book["status"] == "Issued":
            raise LibraryOperationError(
                f"'{book['title']}' is already issued to {book['issued_to']}."
            )
        book["status"] = "Issued"
        book["issued_to"] = member_name
        book["issue_date"] = date.today().isoformat()
        self._save()
        return book

    # ------------------------------------------------------- Return
    def return_book(self, book_id) -> dict:
        book_id = validate_book_id(book_id, [b["id"] for b in self.books])
        book = next(b for b in self.books if b["id"] == book_id)
        if book["status"] == "Available":
            raise LibraryOperationError(f"'{book['title']}' is not currently issued.")
        book["status"] = "Available"
        book["issued_to"] = None
        book["issue_date"] = None
        self._save()
        return book

    # ------------------------------------------------ Data processing
    def get_stats(self) -> dict:
        """Summarize the catalog into simple counts for the Stats view."""
        total = len(self.books)
        issued = sum(1 for b in self.books if b["status"] == "Issued")
        return {"total": total, "available": total - issued, "issued": issued}
