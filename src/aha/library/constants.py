from pathlib import Path

AHA_CONFIG_DIR = Path.home() / ".config" / "aha"
AHA_CONFIG_FILE = AHA_CONFIG_DIR / "config.ini"
DEFAULT_CATALOG_DIR = AHA_CONFIG_DIR / "catalog"

REMOVE_INIT_PY: str = "__init__.py"
PROFILE_SUFFIXES: set[str] = {".yaml", ".yml"}
TEMPLATE_SUFFIXES: set[str] = {".yaml", ".yml"}
HELPER_SUFFIXES: set[str] = {".tpl"}
