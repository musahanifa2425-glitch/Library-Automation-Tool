"""
validators.py
--------------
Input validation utilities for the Library Automation Tool.

Each function validates one piece of user input and raises a
ValidationError with a clear, user-facing message when the input is
invalid. Keeping validation separate from the GUI and business logic
makes it reusable (used by both the GUI and the test suite) and easy
to test in isolation.
"""

import re

from exceptions import ValidationError


def validate_non_empty_text(value, field_name: str, min_len: int = 1, max_len: int = 100) -> str:
    """Validate that a text field is present, non-empty, and within length limits."""
    if value is None:
        raise ValidationError(f"{field_name} is required.")
    value = value.strip()
    if len(value) < min_len:
        raise ValidationError(f"{field_name} cannot be empty.")
    if len(value) > max_len:
        raise ValidationError(f"{field_name} cannot exceed {max_len} characters.")
    return value


def validate_name(value, field_name: str) -> str:
    """Validate a name-like field (book title, author, member name).

    Allows letters, digits, spaces and common punctuation used in
    titles and names (. , ' - & : ( )), rejecting anything else so
    stray control characters or symbols can't corrupt stored records.
    """
    value = validate_non_empty_text(value, field_name, min_len=1, max_len=120)
    if not re.match(r"^[A-Za-z0-9.,'\-&:() ]+$", value):
        raise ValidationError(
            f"{field_name} contains invalid characters. "
            "Use letters, numbers, and basic punctuation only."
        )
    return value


def validate_isbn(value) -> str:
    """Validate an ISBN-10 or ISBN-13 number.

    Accepts digits with optional hyphens/spaces; the final ISBN-10
    check character may be 'X'. Returns the cleaned (digits-only,
    uppercase) ISBN for consistent storage.
    """
    if value is None:
        raise ValidationError("ISBN is required.")
    cleaned = value.strip().upper().replace("-", "").replace(" ", "")
    is_isbn10 = re.match(r"^\d{9}[\dX]$", cleaned)
    is_isbn13 = re.match(r"^\d{13}$", cleaned)
    if not (is_isbn10 or is_isbn13):
        raise ValidationError("ISBN must be a valid 10 or 13 digit number.")
    return cleaned


def validate_book_id(value, existing_ids) -> int:
    """Validate that a book ID is numeric and refers to an existing book."""
    try:
        book_id = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError("Book ID must be a whole number.")
    if book_id not in existing_ids:
        raise ValidationError(f"No book found with ID {book_id}.")
    return book_id
