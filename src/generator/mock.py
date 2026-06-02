"""Local, template-based generator.

This is the default implementation so the full pipeline runs with **no AWS
credentials**. It uses Jinja2 templates to produce a draft and a refined,
metadata-grounded markdown document.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .base import DocGenerator

_TEMPLATE_DIR = Path(__file__).parent / "templates"


class MockGenerator(DocGenerator):
    name = "local-mock"

    def __init__(self, template_dir: Path | str = _TEMPLATE_DIR) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(enabled_extensions=()),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def draft(self, metadata: dict) -> str:
        template = self._env.get_template("draft.md.j2")
        return template.render(**metadata)

    def refine(self, draft: str, metadata: dict) -> str:
        template = self._env.get_template("refined.md.j2")
        return template.render(backend=self.name, **metadata)
