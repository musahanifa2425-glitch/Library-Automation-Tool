"""
data_handler.py
----------------
Handles all persistence for the Library Automation Tool.

Books are stored as a JSON file on disk. This module is the only
place that touches the filesystem, which keeps I/O error handling
contained in one spot rather than scattered through the app.
"""

import json
import os

from exceptions import DataError

DEFAULT_DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "books_data.json"
)


def load_books(file_path: str = DEFAULT_DATA_FILE) -> list:
    """Load the book catalog from a JSON file.

    Returns an empty list if the file does not exist yet (e.g. first
    run). Raises DataError if the file exists but is unreadable or
    corrupted, so the caller can show a clear message instead of
    crashing.
    """
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataError(f"Data file is corrupted and could not be read: {e}")
    except PermissionError:
        raise DataError(f"Permission denied when reading '{file_path}'.")
    except OSError as e:
        raise DataError(f"Could not read data file: {e}")

    if not isinstance(data, list):
        raise DataError("Data file is corrupted: expected a list of books.")
    return data


def save_books(books: list, file_path: str = DEFAULT_DATA_FILE) -> None:
    """Save the book catalog to a JSON file.

    Writes to a temporary file first and then replaces the real file
    atomically, so a crash or power loss mid-write can't leave the
    catalog half-written or corrupted.
    """
    tmp_path = file_path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(books, f, indent=2)
        os.replace(tmp_path, file_path)
    except PermissionError:
        raise DataError(f"Permission denied when writing '{file_path}'.")
    except OSError as e:
        raise DataError(f"Could not save data file: {e}")
