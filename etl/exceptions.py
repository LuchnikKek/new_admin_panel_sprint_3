class ExtractExceptions(Exception):
    """Base class for exceptions to Extract process."""


class EndOfDataException(ExtractExceptions):
    """Extracted service out of data."""
