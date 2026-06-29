"""Git utility helpers used by Aha catalog operations.

This module provides:
- A thin subprocess wrapper for invoking Git commands.
- A robust repository detection helper that supports normal working trees,
  worktrees/submodules, and bare repositories.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def run_git_command(
    args: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Execute a Git command and return the completed subprocess result.

    The command is always executed as: ``git <args...>``.
    Output is captured for caller-side handling and error reporting.

    Args:
        args: Git arguments excluding the leading ``git`` executable.
        cwd: Optional working directory in which to run the Git command.

    Returns:
        subprocess.CompletedProcess[str]:
            Completed process object with captured ``stdout``, ``stderr``,
            and ``returncode`` (no exception is raised on non-zero status).
    """
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def is_git_repository(path: Path) -> bool:
    """Check whether ``path`` is a valid Git repository location.

    This probe is more reliable than checking for a ``.git`` directory because:
    - Worktrees/submodules may store ``.git`` as a file (gitdir pointer).
    - Bare repositories have no working tree and may not have ``.git`` dir.

    Strategy:
    1. Validate ``path`` exists and is a directory.
    2. Run ``git rev-parse --is-inside-work-tree`` in ``path``.
    3. If not inside a working tree, run ``git rev-parse --is-bare-repository``.

    Args:
        path: Filesystem path to validate.

    Returns:
        bool:
            ``True`` if ``path`` is inside a working-tree repository or is a
            bare repository root; otherwise ``False``.
    """
    if not path.exists() or not path.is_dir():
        return False

    inside_work_tree = run_git_command(["rev-parse", "--is-inside-work-tree"], cwd=path)
    if inside_work_tree.returncode == 0 and inside_work_tree.stdout.strip() == "true":
        return True

    is_bare_repository = run_git_command(
        ["rev-parse", "--is-bare-repository"], cwd=path
    )
    return (
        is_bare_repository.returncode == 0
        and is_bare_repository.stdout.strip() == "true"
    )
