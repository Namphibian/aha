from __future__ import annotations

import subprocess
from pathlib import Path


def run_git_command(
    args: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def is_git_repository(path: Path) -> bool:
    """Check if a given path is a valid Git repository."""
    return (path / ".git").is_dir()
