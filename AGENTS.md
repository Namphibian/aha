# AGENTS.md

## Quick Orientation
- `aha` is a Click-based CLI that scaffolds Helm/Kubernetes assets from YAML profiles/templates.
- CLI entrypoint is `aha.main:cli` (`pyproject.toml`, `src/aha/main.py`), with groups: `catalog`, `profiles`, `templates`, `helpers`, `helm`.
- Edit source in `src/`; ignore `build/` (generated distribution artifacts).

## Architecture and Data Flow
- Command modules are split by domain: `src/aha/commands/*/main.py`.
- Shared catalog access is centralized in `src/aha/library/catalog/manager.py`.
- File lookup is catalog-only via `~/.config/aha/config.ini` (`[catalog].path`).
- Profile/template/helper discovery is suffix-driven (`PROFILE_SUFFIXES`, `TEMPLATE_SUFFIXES`, `HELPER_SUFFIXES` in `src/aha/library/constants.py`).
- Current suffix rules: templates are `.yaml/.yml`, helpers are `.tpl`.
- `src/aha/library/catalog/manager.py` raises `AhaCatalogNotInitialisedException` when catalog is missing/invalid.
- `get_profile_data()` / `get_template_data()` / `get_helper_data()` raise exceptions for invalid/missing files.

## Library Utilities (Domain-Specific)
- **Git operations**: `src/aha/library/git/manager.py` — `run_git_command()` (subprocess wrapper), `is_git_repository()` (path validation).
- **Catalog config**: `src/aha/library/catalog/manager.py` — load/save config (`load_config()`, `save_catalog_config()`), read catalog metadata (`get_catalog_path()`, `get_catalog_repo()`, `get_catalog_branch()`, `catalog_manifest_exists()`).
- **Catalog files**: `src/aha/library/catalog/manager.py` — list/get profiles, templates, and helpers from configured catalog path; raises catalog exceptions for missing/invalid files.

## Integration Points
- Git is required for catalog sync; commands call `run_git_command()` in `src/aha/library/git/manager.py` (`subprocess.run(["git", ...])`).
- YAML parsing uses `yaml.safe_load` in `src/aha/library/catalog/manager.py`.
- UI output uses Rich tables/syntax; shared theme is in `src/aha/ui/console.py`.

## Working Commands (Observed)
```bash
pip install -e .
aha --help
aha catalog init --repo <repo-url>
aha catalog status
aha profiles list
aha templates get -t values.yaml
aha helpers list
aha helpers get -n _helpers.tpl
```
- Python runtime target is `>=3.14` (`pyproject.toml`).
- Dev tooling currently declared: `ruff` only; no repo-defined test runner/task script discovered.

## Exit Code Contract (Automation)
- `0`: command completed successfully.
- `1`: runtime operation failed (for example Git command failure in catalog operations).
- `2`: user/config/input precondition failed (for example catalog not initialised, invalid catalog path, non-git catalog path).
- Command handlers use Click exits for non-zero paths so CI/CD scripts can branch reliably.

## Local Conventions to Preserve
- Follow Click patterns already used: grouped commands, explicit options/arguments, early-return validations (`catalog init/update/status`).
- Use `pathlib.Path` + `expanduser()/resolve()` for user paths.
- Reuse `aha.ui.console.console` instead of creating ad-hoc console instances.
- Persist user config under `~/.config/aha/` (`config.ini`, default catalog directory).
- Profile schema example to mirror: `src/resources/profiles/ocp-sn-springboot-rest-api.yaml` (`resources.mandatory`, `resources.optional`, `chart`).

## Known Sharp Edges
- API behavior: catalog `get_*_data()` helpers now raise typed exceptions instead of returning error strings; command handlers should catch and convert to themed output + exit code `2`.
- Import-path rule: keep imports package-qualified (`aha.*`) across modules, including `src/aha/main.py` (for example `from aha.commands.catalog.main import catalog`), to avoid environment-dependent module resolution issues.


