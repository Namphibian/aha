"""Catalog configuration and metadata management.

This module is the single source of truth for reading, validating, and writing
catalog-related configuration stored under ``~/.config/aha/config.ini``.

It exposes two kinds of APIs:
1. Read/write helpers for persisted catalog settings (repo/path/branch).
2. Validation helpers that resolve the configured catalog root and enforce
   that it exists before dependent operations proceed.
"""

from __future__ import annotations

import configparser
import json
from pathlib import Path
from typing import Any, NoReturn

import click
import yaml

from aha.library.constants import (
    AHA_CONFIG_DIR,
    AHA_CONFIG_FILE,
    HELPER_SUFFIXES,
    PROFILE_SUFFIXES,
    REMOVE_INIT_PY,
    TEMPLATE_SUFFIXES,
    VALUES_SUFFIXES,
)


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


def load_config() -> configparser.ConfigParser:
    """Load Aha configuration from disk.

    Reads ``AHA_CONFIG_FILE`` and returns a ``ConfigParser`` instance. If the
    file does not exist yet, an empty config object is returned.

    Returns:
        configparser.ConfigParser: Parsed configuration object.
    """
    config = configparser.ConfigParser()
    config.read(AHA_CONFIG_FILE)
    return config


def save_catalog_config(repo: str, path: Path, branch: str) -> None:
    """Persist catalog configuration values to ``config.ini``.

    Ensures the Aha config directory exists, creates the ``[catalog]`` section
    when missing, then writes ``repo``, ``path``, and ``branch`` fields.

    Args:
        repo: Catalog Git repository URL.
        path: Local filesystem path for the catalog clone.
        branch: Default branch used for catalog operations.
    """
    AHA_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    config = load_config()

    if not config.has_section("catalog"):
        config.add_section("catalog")

    config.set("catalog", "repo", repo)
    config.set("catalog", "path", str(path))
    config.set("catalog", "branch", branch)

    with AHA_CONFIG_FILE.open("w", encoding="utf-8") as config_file:
        config.write(config_file)


def get_catalog_path() -> Path | None:
    """Return configured catalog path from ``[catalog].path``.

    Returns:
        Path | None:
            - ``Path`` when a non-empty path value is configured.
            - ``None`` when section/key is missing or empty.

    Notes:
        This function only reads config intent; it does not verify directory
        existence. Use ``get_catalog_root()`` / ``require_catalog_root()`` for
        existence validation.
    """
    config = load_config()

    if not config.has_section("catalog"):
        return None

    catalog_path = config.get("catalog", "path", fallback="").strip()

    if not catalog_path:
        return None

    return Path(catalog_path)


def get_catalog_root() -> Path | None:
    """Resolve and validate the configured catalog directory.

    Converts the configured path to an absolute path (with ``expanduser`` and
    ``resolve``) and confirms that it exists as a directory.

    Returns:
        Path | None:
            - Resolved catalog directory path when configured and valid.
            - ``None`` when not configured or the directory does not exist.
    """
    catalog_path = get_catalog_path()

    if catalog_path is None:
        return None

    root = catalog_path.expanduser().resolve()

    if not root.is_dir():
        return None

    return root


def require_catalog_root() -> Path:
    """Return validated catalog root or raise a setup exception.

    Returns:
        Path: Resolved catalog root directory.

    Raises:
        AhaCatalogNotInitialisedException: If catalog path is not configured or
            does not resolve to an existing directory.
    """
    root = get_catalog_root()

    if root is None:
        raise AhaCatalogNotInitialisedException(
            "Aha catalog is not initialised. Run: aha catalog init --repo <repo-url>."
        )

    return root


def get_catalog_repo() -> str | None:
    """Return configured catalog repository URL.

    Returns:
        str | None:
            - Repository URL string when configured and non-empty.
            - ``None`` when section/key is missing or empty.
    """
    config = load_config()

    if not config.has_section("catalog"):
        return None

    repo = config.get("catalog", "repo", fallback="").strip()
    return repo or None


def get_catalog_branch() -> str | None:
    """Return configured catalog branch name.

    Returns:
        str | None:
            - Branch name when configured and non-empty.
            - ``None`` when section/key is missing or empty.
    """
    config = load_config()

    if not config.has_section("catalog"):
        return None

    branch = config.get("catalog", "branch", fallback="").strip()
    return branch or None


def catalog_manifest_exists(path: Path) -> bool:
    """Check whether ``catalog.yaml`` exists in the provided directory.

    Args:
        path: Directory expected to contain ``catalog.yaml``.

    Returns:
        bool: ``True`` if ``catalog.yaml`` exists at ``path``, else ``False``.
    """
    return (path / "catalog.yaml").is_file()


def _list_catalog_files(directory: str, allowed_suffixes: set[str]) -> list[str]:
    catalog_directory = require_catalog_root().joinpath(directory)

    if not catalog_directory.is_dir():
        return []

    return sorted(
        path.name
        for path in catalog_directory.iterdir()
        if path.is_file()
        and path.suffix.lower() in allowed_suffixes
        and path.name != REMOVE_INIT_PY
    )


def _catalog_file_path(
    directory: str, name: str, allowed_suffixes: set[str], default_suffix: str
) -> Path:
    catalog_directory = require_catalog_root().joinpath(directory)
    requested_path = catalog_directory.joinpath(name)

    if requested_path.suffix.lower() in allowed_suffixes:
        return requested_path

    return catalog_directory.joinpath(f"{name}{default_suffix}")


def list_profiles() -> list[str]:
    return _list_catalog_files("profiles", PROFILE_SUFFIXES)


def list_templates() -> list[str]:
    return _list_catalog_files("templates", TEMPLATE_SUFFIXES)


def list_values() -> list[str]:
    return _list_catalog_files("values", VALUES_SUFFIXES)


def list_helpers() -> list[str]:
    return _list_catalog_files("helpers", HELPER_SUFFIXES)


def get_profile_data(profile_name: str) -> tuple[str, dict]:
    profile_path = _catalog_file_path(
        directory="profiles",
        name=profile_name,
        allowed_suffixes=PROFILE_SUFFIXES,
        default_suffix=".yaml",
    )

    if profile_path.suffix.lower() not in PROFILE_SUFFIXES:
        raise AhaCatalogInvalidFileTypeException(
            f"Profile '{profile_name}' must be a YAML file."
        )

    if not profile_path.is_file():
        raise AhaCatalogFileNotFoundException(
            f"Profile '{profile_name}' was not found."
        )

    yaml_str: str = profile_path.read_text(encoding="utf-8")
    return yaml_str, yaml.safe_load(yaml_str)


def get_template_data(template_name: str) -> str:
    template_path = _catalog_file_path(
        directory="templates",
        name=template_name,
        allowed_suffixes=TEMPLATE_SUFFIXES,
        default_suffix=".yaml",
    )

    if template_path.suffix.lower() not in TEMPLATE_SUFFIXES:
        raise AhaCatalogInvalidFileTypeException(
            f"Template '{template_name}' must be a YAML or TPL file."
        )

    if not template_path.is_file():
        raise AhaCatalogFileNotFoundException(
            f"Template '{template_name}' was not found."
        )

    data_str: str = template_path.read_text(encoding="utf-8")
    return data_str


def get_values_data(template_name: str) -> tuple[str, Any]:
    template_path = _catalog_file_path(
        directory="values",
        name=template_name,
        allowed_suffixes=VALUES_SUFFIXES,
        default_suffix=".json",
    )

    if template_path.suffix.lower() not in VALUES_SUFFIXES:
        raise AhaCatalogInvalidFileTypeException(
            f"Template '{template_name}' must be a YAML or TPL file."
        )

    if not template_path.is_file():
        raise AhaCatalogFileNotFoundException(
            f"Template '{template_name}' was not found."
        )

    data_str: str = template_path.read_text(encoding="utf-8")
    return data_str, json.loads(data_str)


def get_helper_data(helper_name: str) -> Any:
    helper_path = _catalog_file_path(
        directory="helpers",
        name=helper_name,
        allowed_suffixes=HELPER_SUFFIXES,
        default_suffix=".tpl",
    )

    if helper_path.suffix.lower() not in HELPER_SUFFIXES:
        raise AhaCatalogInvalidFileTypeException(
            f"Helper '{helper_name}' must be a YAML or TPL file."
        )

    if not helper_path.is_file():
        raise AhaCatalogFileNotFoundException(f"Helper '{helper_name}' was not found.")

    yaml_str: str = helper_path.read_text(encoding="utf-8")
    return yaml_str
