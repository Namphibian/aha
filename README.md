# Aha

A templating and project‑scaffolding tool inspired by the Sotho word “aha” — to build.

Aha is a Python‑based command‑line tool designed to help you build, assemble, and shape project structures with ease. Whether you're generating Helm‑ready Kubernetes layouts, bootstrapping microservices, or assembling internal templates, Aha gives you a clean, expressive workflow for creating consistent project foundations.

### Aha focuses on:

Simplicity — clear commands, predictable output

Structure — opinionated scaffolding that keeps projects tidy

Flexibility — bring your own templates, values, and patterns

Speed — generate full project layouts in seconds

### Why “Aha”?

In Sotho languages, “aha” means to build.
This tool embraces that spirit — helping you build reliable, repeatable project structures with minimal friction.

### Features

Template‑driven project generation

Configurable resource loading

Support for YAML, Jinja2, and custom template engines

CLI‑first design using Click

Extensible layout definitions

### Catalog File Types

When loading files from the configured catalog:

- Profiles: `.yaml`, `.yml`
- Templates: `.yaml`, `.yml`
- Helpers: `.tpl`

These suffix rules are enforced in `src/aha/library/constants.py` and used by catalog file-discovery/get commands.

### Exit Codes (Pipeline Contract)

`aha` commands are safe to use in CI/CD scripts (Azure DevOps, Jenkins, GitHub Actions) with this contract:

- `0`: command completed successfully
- `1`: runtime operation failed (for example Git clone/pull/status command failure)
- `2`: user/config/input precondition failed (for example catalog not initialised, invalid configured path, non-git catalog path)

Common automation guard:

```bash
aha templates list
case $? in
  0) echo "ok" ;;
  1) echo "runtime failure" ; exit 1 ;;
  2) echo "configuration/input failure" ; exit 2 ;;
esac
```
