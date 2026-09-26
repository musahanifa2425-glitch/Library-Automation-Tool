"""
gui.py
-------
Tkinter GUI for the Library Automation Tool.

This module is only responsible for presentation: it renders the
catalog in a table, collects input through simple dialogs, and shows
success/error feedback. All real logic lives in BookManager, so the
UI stays thin and the business rules stay testable without a display.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from book_manager import BookManager
from exceptions import DataError, LibraryOperationError, ValidationError


class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Automation Tool By Musa")
        self.geometry("780x480")
        self.minsize(600, 360)

        self.manager = None
        try:
            self.manager = BookManager()
        except DataError as e:
            messagebox.showerror("Startup error", str(e))

        self._build_widgets()
        self.refresh_table()

    # ------------------------------------------------------- Layout
    def _build_widgets(self):
        toolbar = tk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)

        actions = [
            ("Add Book", self.add_book_dialog),
            ("Remove Book", self.remove_book_dialog),
            ("Issue Book", self.issue_book_dialog),
            ("Return Book", self.return_book_dialog),
            ("Refresh", self.refresh_table),
            ("Stats", self.show_stats),
        ]
        for label, cmd in actions:
            tk.Button(toolbar, text=label, command=cmd).pack(side="left", padx=4)

        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=8)
        tk.Label(search_frame, text="Search (title / author / ISBN):").pack(side="left")
        self.search_var = tk.StringVar()
        entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        entry.pack(side="left", padx=4)
        entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        columns = ("id", "title", "author", "isbn", "status", "issued_to")
        headings = {
            "id": "ID", "title": "Title", "author": "Author",
            "isbn": "ISBN", "status": "Status", "issued_to": "Issued To",
        }
        widths = {"id": 40, "title": 220, "author": 150, "isbn": 110, "status": 80, "issued_to": 120}

        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    # ------------------------------------------------------ Refresh
    def refresh_table(self):
        if not self.manager:
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        for book in self.manager.search_books(self.search_var.get()):
            self.tree.insert("", "end", values=(
                book["id"], book["title"], book["author"],
                book["isbn"], book["status"], book["issued_to"] or "-",
            ))

    # ------------------------------------------------------- Dialogs
    def _prompt(self, title, prompt):
        return simpledialog.askstring(title, prompt, parent=self)

    def add_book_dialog(self):
        title = self._prompt("Add Book", "Title:")
        if title is None:
            return
        author = self._prompt("Add Book", "Author:")
        if author is None:
            return
        isbn = self._prompt("Add Book", "ISBN (10 or 13 digits):")
        if isbn is None:
            return
        try:
            self.manager.add_book(title, author, isbn)
            messagebox.showinfo("Success", "Book added successfully.")
            self.refresh_table()
        except (ValidationError, LibraryOperationError, DataError) as e:
            messagebox.showerror("Could not add book", str(e))

    def remove_book_dialog(self):
        book_id = self._prompt("Remove Book", "Book ID to remove:")
        if book_id is None:
            return
        try:
            book = self.manager.remove_book(book_id)
            messagebox.showinfo("Success", f"Removed '{book['title']}'.")
            self.refresh_table()
        except (ValidationError, LibraryOperationError, DataError) as e:
            messagebox.showerror("Could not remove book", str(e))

    def issue_book_dialog(self):
        book_id = self._prompt("Issue Book", "Book ID to issue:")
        if book_id is None:
            return
        member = self._prompt("Issue Book", "Issue to (member name):")
        if member is None:
            return
        try:
            book = self.manager.issue_book(book_id, member)
            messagebox.showinfo("Success", f"'{book['title']}' issued to {member}.")
            self.refresh_table()
        except (ValidationError, LibraryOperationError, DataError) as e:
            messagebox.showerror("Could not issue book", str(e))

    def return_book_dialog(self):
        book_id = self._prompt("Return Book", "Book ID to return:")
        if book_id is None:
            return
        try:
            book = self.manager.return_book(book_id)
            messagebox.showinfo("Success", f"'{book['title']}' returned.")
            self.refresh_table()
        except (ValidationError, LibraryOperationError, DataError) as e:
            messagebox.showerror("Could not return book", str(e))

    def show_stats(self):
        if not self.manager:
            return
        stats = self.manager.get_stats()
        messagebox.showinfo(
            "Library Stats",
            f"Total books: {stats['total']}\n"
            f"Available: {stats['available']}\n"
            f"Issued: {stats['issued']}",
        )


if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()
