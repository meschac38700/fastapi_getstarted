from os.path import getmtime
from pathlib import Path
from typing import Generator

from jinja2 import BaseLoader, Environment, TemplateNotFound

from core.templating.exceptions import ManyTemplateFoundError
from settings import settings


class BaseTemplateLoader(BaseLoader):
    """Abstract base class for template loaders."""

    def __init__(self):
        self.template_dirname = settings.TEMPLATE_DIR

    def _get_template_dirs(self) -> Generator[Path, None, None]:
        raise NotImplementedError()

    def retrieve_template(self, template_name: str):
        """Retrieve a template by name.

        example:
            >>> retrieve_template("/index.html")
            >>> ManyTemplateFoundError
            >>> retrieve_template("/users/index.html")
            >>> Path('/.../apps/users/templates/users/index.html')
        """
        templates_found = [
            template_dir / template_name
            for template_dir in self._get_template_dirs()
            if (template_dir / template_name).exists()
        ]
        if not templates_found:
            raise TemplateNotFound(template_name)

        if len(templates_found) > 1:
            raise ManyTemplateFoundError(
                f"Ambiguous template name, many templates found: {templates_found}"
            )

        return templates_found[0]

    def get_source(self, environment: Environment, template: str):
        path = self.retrieve_template(template)
        last_modification_time = getmtime(path)
        with open(path) as f:
            source = f.read()
        return source, path, lambda: last_modification_time == getmtime(path)
