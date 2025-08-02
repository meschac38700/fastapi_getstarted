import glob
from functools import lru_cache
from pathlib import Path
from typing import Generator

from jinja2 import Environment, select_autoescape

from core.services import files as file_services
from core.templating.loaders._base import BaseTemplateLoader


class AppTemplateLoader(BaseTemplateLoader):
    """Load templates from 'apps' package.

    Docs: https://jinja.palletsprojects.com/en/stable/api/#jinja2.ChoiceLoader
    Docs loader: https://jinja.palletsprojects.com/en/stable/api/#loaders
    """

    def _get_template_dirs(self) -> Generator[Path, None, None]:
        for app_template_dir in file_services.get_application_paths(
            self.template_dirname
        ):
            yield app_template_dir / self.template_dirname

    def list_templates(self) -> list[str]:
        """List all available templates."""

        return sum(
            [
                [
                    # make the template path relative to the app template directory
                    str(Path(template_path).relative_to(app_template_dir))
                    for template_path in glob.glob(
                        str(app_template_dir / "**" / "*.html"), recursive=True
                    )
                ]
                for app_template_dir in self._get_template_dirs()
            ],
            [],
        )


@lru_cache
def environment():
    return Environment(
        loader=AppTemplateLoader(),
        autoescape=select_autoescape(),
        extensions=file_services.apps.retrieve_template_tags(),
    )
