import tomllib
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

ROOT = Path("")
TEMPLATE_DIR = ROOT / "templates"
TARGET_DIRS = ["apps", "libs"]

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("pyproject.j2")


def load_existing(path: Path) -> dict[str, Any]:
    """

    Args:
        path:

    Returns:

    """
    try:
        return tomllib.loads(path.read_text())
    except Exception:
        return {}


def extract_metadata(data: dict[str, Any], path: Path) -> dict[str, Any]:
    """

    Args:
        data:
        path:

    Returns:

    """
    project = data.get("project", {})

    return {
        "name": project.get("name", path.parent.name),
        "description": project.get("description", ""),
        "dependencies": project.get("dependencies", []),
    }


def render_file(path: Path) -> None:
    """

    Args:
        path:
    """
    data = load_existing(path)
    meta = extract_metadata(data, path)

    rendered = template.render(**meta)

    path.write_text(rendered)


def main() -> None:
    """Render template-backed pyproject files under workspace package roots."""
    for d in TARGET_DIRS:
        for path in (ROOT / d).rglob("pyproject.toml"):
            render_file(path)


if __name__ == "__main__":
    main()
