from __future__ import annotations


class AhaCatalogNotInitialisedException(RuntimeError):
    """Raised when catalog operations are requested before setup is valid.

    This is used by callers that require a usable catalog root directory and
    cannot continue safely when the catalog config is missing or invalid.
    """


class AhaCatalogDataException(RuntimeError):
    """Raised for catalog data access and validation errors."""


class AhaCatalogInvalidFileTypeException(AhaCatalogDataException):
    """Raised when a requested catalog file name has an invalid suffix."""


class AhaCatalogFileNotFoundException(AhaCatalogDataException):
    """Raised when a requested catalog file is not found."""

