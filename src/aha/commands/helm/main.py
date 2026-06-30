import click
from pathlib import Path
from typing import Any

import yaml

from aha.library.catalog.manager import (
    AhaCatalogDataException,
    AhaCatalogNotInitialisedException,
)
from aha.library.catalog.manager import (
    get_helper_data,
    get_profile_data,
    get_template_data,
    get_values_data,
)
from aha.ui.console import console
from aha.ui.console_exception_helper import exit_catalog_not_initialised


@click.group()
@click.pass_context
def helm(ctx):
    """Work with Helm."""
    pass


@helm.group()
@click.pass_context
def generate(ctx):
    """Generate a Helm resource"""
    pass


@generate.command("chart")
@click.pass_context
@click.argument("name", type=str, required=True)
@click.option("--profile", "-p", type=str, required=True)
@click.option("--output-path", "-o", type=click.Path(path_type=Path), required=True)
def chart(ctx, name: str, profile: str, output_path: Path):
    """Generate a Helm chart"""
    try:
        _, profile_data = get_profile_data(profile)
        profile_name = profile_data.get("name", profile)
        console.print(f"[info]Generating Helm chart for profile {profile_name}[/info]")
        console.print(f"[info]Chart name: {name}[/info]")
        console.print(f"[info]Output path: {output_path}[/info]")

        prepare_new_helm_chart_folder(output_path)

        chart_file = write_profile_chart_yaml_file(name, output_path, profile_data)
        console.print(f"[success]Generated[/success] [path]{chart_file}[/path]")

        templates_dir = write_profile_templates_to_chart(output_path, profile_data)
        console.print(
            f"[success]Generated[/success] all templates to [path]{templates_dir}[/path]"
        )
        write_profile_helpers_to_chart(profile_data, templates_dir)

        console.print(
            f"[success]Generated[/success] all helpers to [path]{templates_dir}[/path]"
        )
        values_schema_name: Any = profile_data.get("values")
        if not isinstance(values_schema_name, str):
            console.print("[error]Profile 'values' must be a schema file name.[/error]")
            raise click.exceptions.Exit(2)

        values_file = write_profile_values_yaml_file(output_path, values_schema_name)
        console.print(f"[success]Generated[/success] [path]{values_file}[/path]")

        notes_file = write_profile_notes_file(output_path, profile_data)
        if notes_file is not None:
            console.print(f"[success]Generated[/success] [path]{notes_file}[/path]")

        readme_file = write_profile_readme_file(output_path, profile_data)
        if readme_file is not None:
            console.print(f"[success]Generated[/success] [path]{readme_file}[/path]")

    except AhaCatalogNotInitialisedException:
        exit_catalog_not_initialised()
    except AhaCatalogDataException as exc:
        console.print(f"[error]{exc}[/error]")
        raise click.exceptions.Exit(2)


def prepare_new_helm_chart_folder(output_path: Path):
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    elif not output_path.is_dir():
        console.print(f"[error]Output path {output_path} is not a directory.[/error]")
        raise click.exceptions.Exit(2)
    elif any(output_path.iterdir()):
        console.print(f"[error]Output path {output_path} is not empty.[/error]")
        console.print(
            "[subtle]Please manually delete the folder contents or choose a different output path.[/subtle]"
        )
        raise click.exceptions.Exit(2)


def write_profile_helpers_to_chart(profile_data, templates_dir: Path):
    helper_names: Any = profile_data.get("helpers", [])
    if not isinstance(helper_names, list):
        console.print("[error]Profile 'helpers' must be a list.[/error]")
        raise click.exceptions.Exit(2)

    for helper_name in helper_names:
        if not isinstance(helper_name, str):
            console.print("[error]Helper names must be strings.[/error]")
            raise click.exceptions.Exit(2)

        helper_str = get_helper_data(helper_name)
        helper_file_name = (
            helper_name if Path(helper_name).suffix else f"{helper_name}.tpl"
        )
        helper_target = templates_dir / helper_file_name
        helper_target.write_text(helper_str, encoding="utf-8")


def write_profile_templates_to_chart(output_path: Path, profile_data) -> Path:
    templates_dir = output_path / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)

    templates_data: Any = profile_data.get("templates", {})
    if not isinstance(templates_data, dict):
        console.print("[error]Profile 'templates' must be an object.[/error]")
        raise click.exceptions.Exit(2)

    mandatory_templates = templates_data.get("mandatory", [])
    optional_templates = templates_data.get("optional", [])
    if not isinstance(mandatory_templates, list) or not isinstance(
        optional_templates, list
    ):
        console.print("[error]Profile template groups must be lists.[/error]")
        raise click.exceptions.Exit(2)

    template_names = [*mandatory_templates, *optional_templates]
    for template_name in template_names:
        if not isinstance(template_name, str):
            console.print("[error]Template names must be strings.[/error]")
            raise click.exceptions.Exit(2)

        template_str = get_template_data(template_name)
        template_file_name = (
            template_name if Path(template_name).suffix else f"{template_name}.yaml"
        )
        template_target = templates_dir / template_file_name
        template_target.write_text(template_str, encoding="utf-8")
    return templates_dir


def write_profile_chart_yaml_file(name: str, output_path: Path, profile_data) -> Path:
    chart_data: Any = profile_data.get("chart")

    if not isinstance(chart_data, dict):
        console.print("[error]Profile is missing a valid 'chart' object.[/error]")
        raise click.exceptions.Exit(2)

    # CLI argument is the generated chart name, so it overrides profile default.
    chart_payload = dict(chart_data)
    chart_payload["name"] = name

    chart_file = output_path / "Chart.yaml"
    try:
        chart_file.write_text(
            yaml.safe_dump(chart_payload, sort_keys=False),
            encoding="utf-8",
        )
    except OSError as exc:
        console.print(f"[error]Failed to write {chart_file}: {exc}[/error]")
        raise click.exceptions.Exit(1)
    return chart_file


def write_profile_values_yaml_file(output_path: Path, values_schema_name: str) -> Path:
    _, values_schema = get_values_data(values_schema_name)

    if not isinstance(values_schema, dict):
        console.print("[error]Values schema must be a JSON object.[/error]")
        raise click.exceptions.Exit(2)

    values_payload = _extract_defaults_from_schema(values_schema)
    if values_payload is None:
        values_payload = {}

    values_file = output_path / "values.yaml"
    try:
        values_file.write_text(
            yaml.safe_dump(values_payload, sort_keys=False),
            encoding="utf-8",
        )
    except OSError as exc:
        console.print(f"[error]Failed to write {values_file}: {exc}[/error]")
        raise click.exceptions.Exit(1)

    return values_file


def write_profile_notes_file(output_path: Path, profile_data) -> Path | None:
    notes: Any = profile_data.get("notes")

    if notes is None:
        return None

    if not isinstance(notes, str):
        console.print("[error]Profile 'notes' must be a string.[/error]")
        raise click.exceptions.Exit(2)

    notes_file = output_path / "templates" / "NOTES.txt"
    try:
        notes_file.write_text(notes, encoding="utf-8")
    except OSError as exc:
        console.print(f"[error]Failed to write {notes_file}: {exc}[/error]")
        raise click.exceptions.Exit(1)

    return notes_file


def write_profile_readme_file(output_path: Path, profile_data) -> Path | None:
    readme: Any = profile_data.get("readme")

    if readme is None:
        return None

    if not isinstance(readme, str):
        console.print("[error]Profile 'readme' must be a string.[/error]")
        raise click.exceptions.Exit(2)

    readme_file = output_path / "README.md"
    try:
        readme_file.write_text(readme, encoding="utf-8")
    except OSError as exc:
        console.print(f"[error]Failed to write {readme_file}: {exc}[/error]")
        raise click.exceptions.Exit(1)

    return readme_file


def _extract_defaults_from_schema(schema: Any) -> Any:
    if not isinstance(schema, dict):
        return None

    if "default" in schema:
        return schema["default"]

    schema_type = schema.get("type")

    if schema_type == "object" or "properties" in schema:
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            return {}

        defaults: dict[str, Any] = {}
        for key, property_schema in properties.items():
            default_value = _extract_defaults_from_schema(property_schema)
            if default_value is not None:
                defaults[key] = default_value
        return defaults

    if schema_type == "array":
        items_schema = schema.get("items")
        item_default = _extract_defaults_from_schema(items_schema)
        if item_default is None:
            return []
        return [item_default]

    return None


