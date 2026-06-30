import subprocess
import tempfile
import unittest
from pathlib import Path

from aha.library.git.manager import is_git_repository, run_git_command


class GitManagerBehavior(unittest.TestCase):
    def test_run_git_command_returns_completed_process_for_valid_git_command(self):
        result = run_git_command(["--version"])

        self.assertEqual(result.returncode, 0)
        self.assertIn("git version", result.stdout.lower())

    def test_run_git_command_captures_non_zero_exit_for_invalid_git_command(self):
        result = run_git_command(["definitely-not-a-real-git-flag"])

        self.assertNotEqual(result.returncode, 0)
        self.assertIsInstance(result.stderr, str)
        self.assertNotEqual(result.stderr.strip(), "")

    def test_is_git_repository_returns_false_for_missing_path(self):
        missing_path = Path(tempfile.gettempdir()) / "aha-missing-git-repo-path"

        self.assertFalse(is_git_repository(missing_path))

    def test_is_git_repository_returns_false_for_regular_file_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "not-a-directory.txt"
            file_path.write_text("content", encoding="utf-8")

            self.assertFalse(is_git_repository(file_path))

    def test_is_git_repository_returns_false_for_directory_that_is_not_a_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertFalse(is_git_repository(Path(tmpdir)))

    def test_is_git_repository_returns_true_for_standard_work_tree_repository(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            repo_path.mkdir(parents=True, exist_ok=True)

            init_result = subprocess.run(
                ["git", "init"],
                cwd=repo_path,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0)

            self.assertTrue(is_git_repository(repo_path))

    def test_is_git_repository_returns_true_for_subdirectory_inside_work_tree(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            nested_path = repo_path / "nested" / "path"
            nested_path.mkdir(parents=True, exist_ok=True)

            init_result = subprocess.run(
                ["git", "init"],
                cwd=repo_path,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0)

            self.assertTrue(is_git_repository(nested_path))

    def test_is_git_repository_returns_true_for_bare_repository(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bare_repo_path = Path(tmpdir) / "bare.git"

            init_result = subprocess.run(
                ["git", "init", "--bare", str(bare_repo_path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(init_result.returncode, 0)

            self.assertTrue(is_git_repository(bare_repo_path))



