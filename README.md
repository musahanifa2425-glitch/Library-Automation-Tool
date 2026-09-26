# Library Automation Tool

A desktop library management application built with Python and Tkinter,
developed as a Python development internship project.

## Features

- **Add books** — title, author, ISBN (validated, duplicate ISBNs rejected)
- **Remove books** — blocked if the book is currently issued
- **Search** — live filter across title, author, and ISBN
- **Issue books** — records who a book is issued to and the issue date
- **Return books** — clears the issue record and marks the book available
- **Stats** — quick summary of total / available / issued counts

## Project Structure

```
library_automation/
├── main.py            # Entry point — run this to launch the app
├── gui.py             # Tkinter GUI (presentation layer only)
├── book_manager.py     # Core business logic (CRUD, issue/return, stats)
├── data_handler.py     # JSON file persistence (load/save, atomic writes)
├── validators.py       # Input validation rules
├── exceptions.py       # Custom exception types
├── books_data.json     # Data file (sample records included)
├── test_library.py     # Unit test suite
└── README.md
```

Splitting the code this way means each module has one job: `gui.py` never
touches the filesystem, `data_handler.py` never validates input, and
`validators.py` has no dependency on Tkinter at all — which is what makes
`book_manager.py` and `validators.py` fully unit-testable without a display.

## How to Run

Requires Python 3.8+. Tkinter ships with most standard Python installs;
on some Linux distributions you may need to install it separately:

```bash
# Debian/Ubuntu, only if you get "No module named tkinter"
sudo apt-get install python3-tk
```

Then launch the app:

```bash
python main.py
```

A sample catalog of 3 books is included in `books_data.json` so the app
has data to show on first launch. Delete that file (or edit it) to start
from an empty catalog.

## Design Decisions

- **Storage**: a single JSON file (`books_data.json`), chosen for
  simplicity and human-readability over SQLite, since the scope here is
  single-user and doesn't need concurrent access or complex queries.
- **Atomic writes**: `data_handler.py` writes to a `.tmp` file and then
  renames it over the real file, so an interrupted write (crash, power
  loss) can never leave `books_data.json` half-written.
- **Validation as its own module**: `validators.py` is shared by both the
  GUI and the test suite, so the exact same rules apply everywhere and
  are tested independently of Tkinter.
- **Custom exceptions**: `ValidationError`, `DataError`, and
  `LibraryOperationError` let the GUI catch precisely the failures it
  expects and show a friendly `messagebox`, without hiding real bugs
  behind a blanket `except Exception`.

## Error Handling Covered

- Empty / invalid title, author, member name (bad characters, too long)
- Invalid or malformed ISBN (must be 10 or 13 digits)
- Duplicate ISBN when adding a book
- Non-numeric or non-existent book ID
- Removing a book that is currently issued
- Issuing a book that's already issued
- Returning a book that isn't issued
- Corrupted or unreadable data file (caught and reported, not crashed)
- File permission errors on read/write

## Testing

The test suite covers validators and all `BookManager` operations,
using a temporary JSON file so tests never touch the real data file.

```bash
python -m unittest test_library.py -v
```

17 tests, all passing — covering the happy path and every error
condition listed above.

## Possible Future Improvements

- Member management (a dedicated member list, not just a name string)
- Due dates and overdue/fine tracking
- Multiple copies per title (quantity instead of one record per copy)
- Export catalog to CSV for reporting
- Switch storage to SQLite if the catalog grows large or needs
  concurrent multi-user access
