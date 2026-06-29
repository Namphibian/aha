from rich.console import Console
from rich.theme import Theme

aha_theme = Theme(
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

console = Console(theme=aha_theme)
