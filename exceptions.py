"""
exceptions.py
--------------
Custom exception types used across the Library Automation Tool.

Keeping these separate from generic Python exceptions lets the GUI
layer catch exactly the failures it expects (bad input, bad data
file, invalid operation) and show a clean message to the user,
while letting truly unexpected bugs surface normally instead of
being silently swallowed.
"""


class ValidationError(Exception):
    """Raised when user-provided input fails a validation rule."""
    pass


class DataError(Exception):
    """Raised when reading or writing the JSON data file fails."""
    pass


class LibraryOperationError(Exception):
    """Raised for invalid library operations, e.g. issuing a book
    that is already issued, or removing a book that is out on loan."""
    pass
