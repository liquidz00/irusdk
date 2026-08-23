"""Sphinx configuration."""

import inspect
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("../src"))

from irusdk.__about__ import __version__  # noqa: E402

project = "irusdk"
author = "Andrew Lerman"
copyright = "2026, Andrew Lerman"
release = __version__
version = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_iconify",
    "sphinxcontrib.autodoc_pydantic",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

myst_enable_extensions = ["colon_fence", "deflist", "substitution"]
myst_heading_anchors = 3

autosectionlabel_prefix_document = True

add_module_names = False
autodoc_typehints = "both"
autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "show-inheritance": True}
toc_object_entries_show_parents = "hide"

# The models are response shapes, not settings: the JSON schema and config tables are noise.
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_member_order = "bysource"
autodoc_pydantic_field_list_validators = False

# httpx is mkdocs-based and publishes no objects.inv, so it cannot be linked here.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest", None),
}

html_theme = "shibuya"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_title = f"irusdk {release}"

html_theme_options = {
    "accent_color": "violet",
    "color_mode": "auto",
    "github_url": "https://github.com/liquidz00/irusdk",
    "nav_links": [
        {"title": "Guide", "url": "guide/quickstart"},
        {"title": "Reference", "url": "reference/index"},
        {
            "title": "Resources",
            "url": "https://api-docs.iru.com",
            "children": [
                {"title": "Iru API docs", "url": "https://api-docs.iru.com"},
                {
                    "title": "Changelog",
                    "url": "https://github.com/liquidz00/irusdk/blob/main/CHANGELOG.md",
                },
                {"title": "PyPI", "url": "https://pypi.org/project/irusdk/"},
            ],
        },
    ],
}

html_context = {
    "source_type": "github",
    "source_user": "liquidz00",
    "source_repo": "irusdk",
}

_REPO = "https://github.com/liquidz00/irusdk"
_SRC_ROOT = Path(__file__).resolve().parent.parent / "src"


def linkcode_resolve(domain: str, info: dict) -> str | None:
    """
    Point the ``[source]`` links at GitHub, deep-linking to the exact lines.

    :param domain: The documented domain; only ``py`` is resolved.
    :param info: Sphinx's object description.
    :return: The GitHub URL, or ``None`` when the object cannot be located.
    """
    if domain != "py" or not info.get("module"):
        return None

    obj = sys.modules.get(info["module"])
    for part in info["fullname"].split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            return None

    try:
        source_file = inspect.getsourcefile(inspect.unwrap(obj))
        lines, start = inspect.getsourcelines(inspect.unwrap(obj))
    except (TypeError, OSError):
        return None
    if not source_file:
        return None

    relative = Path(source_file).resolve().relative_to(_SRC_ROOT.parent)
    branch = "main" if "dev" not in release else "develop"
    return f"{_REPO}/blob/{branch}/{relative}#L{start}-L{start + len(lines) - 1}"
