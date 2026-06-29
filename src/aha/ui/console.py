"""Shared Rich console setup for Aha CLI output.

This module centralizes:
- The global output theme (`AHA_THEME`).
- Lazy creation of a shared `Console` instance.
- Optional runtime configuration hooks for tests/callers.
- Backward-compatible `console.print(...)` call style via proxy.

Design notes:
- Console creation is deferred until first use to avoid import-time side effects.
- `configure_console(...)` can be used before first output to override defaults
  (e.g., `record=True`, `force_terminal=False`, custom width, stderr routing).
- `reset_console()` is provided primarily for test isolation.
"""

from rich.console import Console
from rich.theme import Theme

# Global Rich theme used by default when constructing console instances.
AHA_THEME = Theme(
    {
        # Core semantic styles
        "info": "bold bright_blue",
        "warning": "bold yellow",
        "error": "bold bright_red",
        "success": "bold green",
        # Builder aesthetic
        "key": "bold bright_white",
        "value": "bright_cyan",
        "path": "italic bright_black",
        "highlight": "bold bright_yellow",
        # Sotho cultural tones
        "sotho.blue": "bold blue",
        "sotho.red": "bold red",
        "sotho.gold": "bold yellow",
        "sotho.white": "bold white",
        "sotho.black": "bold black",
        # Structural / UI elements
        "header": "bold bright_white on black",
        "subtle": "dim bright_black",
        "accent": "bold bright_magenta",
    }
)

# Cached singleton console instance created lazily by `get_console()`.
_console_instance: Console | None = None

# Deferred constructor options merged into `create_console(...)` at first use.
# Example options: record=True, force_terminal=False, width=120, stderr=True
_console_options: dict = {}


def create_console(theme: Theme | None = None, **kwargs) -> Console:
    """Create and return a new Rich Console instance.

    Args:
        theme: Optional Rich theme override. If omitted, `AHA_THEME` is used.
        **kwargs: Arbitrary `rich.console.Console` constructor options.

    Returns:
        Console: A newly constructed Rich Console.
    """
    return Console(theme=theme or AHA_THEME, **kwargs)


def configure_console(**kwargs) -> None:
    """Set default options for lazy console construction.

    These options are applied when `get_console()` creates the singleton for the
    first time.

    Important:
        Call this before first console use. If the console was already created,
        call `reset_console()` first, then configure again.

    Args:
        **kwargs: Arbitrary `Console(...)` constructor options.
    """
    _console_options.update(kwargs)


def reset_console() -> None:
    """Clear the cached singleton console instance.

    Useful in tests to avoid shared state between test cases.
    """
    global _console_instance
    _console_instance = None


def get_console() -> Console:
    """Return the shared console instance, creating it on first access.

    Returns:
        Console: Lazily initialized singleton Rich console.
    """
    global _console_instance

    if _console_instance is None:
        _console_instance = create_console(**_console_options)

    assert _console_instance is not None
    return _console_instance


class _ConsoleProxy:
    """Proxy object preserving `console.<method>` usage with lazy backend.

    This allows existing call sites such as:
        `console.print(...)`
    while still deferring actual Console instantiation until needed.
    """

    def __getattr__(self, name):
        """Forward unknown attributes/methods to the lazily created console."""
        return getattr(get_console(), name)


# Backward-compatible exported object used across command modules.
# Accessing any attribute triggers lazy singleton initialization.
console = _ConsoleProxy()
