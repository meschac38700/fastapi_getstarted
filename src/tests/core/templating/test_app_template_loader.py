import contextlib
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from jinja2 import TemplateNotFound

from core.templating.exceptions import ManyTemplateFoundError
from core.templating.loaders import app_template_loader
from core.unittest.async_case import AsyncTestCase


class TestAppTemplateLoader(AsyncTestCase):
    test_template_app = Path(__file__).parent

    def _create_template_file(
        self,
        filename: str,
        app_template: Path | None = None,
        template_dir: str | None = None,
    ):
        _app_template = app_template or self.test_template_app
        _template_dir = template_dir or app_template_loader.loader.template_dirname
        _file = _app_template / _template_dir / filename
        _file.touch(exist_ok=True)
        assert _file.is_file()
        return _file

    def _mock_test_template_dir(
        self,
        mock_file_services: MagicMock,
        template_dirname: str,
        application_dirs: list[Path] | None = None,
    ):
        # mock application path to return the current parent dir, for tests purpose

        app_dirs = application_dirs or [self.test_template_app]

        test_template_dir = self.test_template_app / template_dirname

        # make sure the directory does not exist
        shutil.rmtree(test_template_dir, ignore_errors=True)
        test_template_dir.mkdir(exist_ok=True, parents=True)
        assert test_template_dir.is_dir()
        mock_file_services.get_application_paths = MagicMock(return_value=app_dirs)

    @contextlib.contextmanager
    def mock_template_dir(
        self, template_dirname: str = "templates", app_dirs: list[Path] | None = None
    ):
        with patch("core.templating.loaders.apps.file_services") as mock_file_services:
            self._mock_test_template_dir(mock_file_services, template_dirname, app_dirs)
            yield
            # clear files/folders
            shutil.rmtree(
                str(
                    self.test_template_app / app_template_loader.loader.template_dirname
                ),
                ignore_errors=True,
            )

    def test_simple_load_template(self):
        with self.mock_template_dir():
            index_file = self._create_template_file("index.html")

            expected_text = "<h1>Hello, world!</h1>"
            index_file.write_text(expected_text)

            template = app_template_loader.get_template(index_file.name)
            assert template.render() == expected_text

    def test_load_template_from_custom_template_dir(self):
        custom_template_dir = "pages"
        with patch.object(
            app_template_loader.loader, "template_dirname", custom_template_dir
        ):
            with self.mock_template_dir(custom_template_dir):
                sub_folder = self.test_template_app / custom_template_dir / "email"
                sub_folder.mkdir(exist_ok=True)
                index_file = self._create_template_file(
                    "index.html", template_dir=str(sub_folder)
                )

                expected_text = "<h1>Custom template folder!</h1>"
                index_file.write_text(expected_text)

                template = app_template_loader.get_template(
                    sub_folder.stem + "/" + index_file.name
                )
                assert template.render() == expected_text

    def test_load_template_not_found(self):
        with self.mock_template_dir():
            index_file = self.test_template_app / "templates" / "not_found.html"

            with pytest.raises(TemplateNotFound) as e:
                app_template_loader.get_template(index_file.name)
            assert index_file.name in str(e)

    def test_load_template_with_context(self):
        with self.mock_template_dir():
            index_file = self._create_template_file("index.html")

            text = "<h1>Hello {{name}}!</h1>"
            index_file.write_text(text)

            template = app_template_loader.get_template(index_file.name)
            name = "John DOE"
            expected_text = text.replace("{{name}}", name)
            assert template.render(name=name) in expected_text

    def test_load_template_error_many_templates_found(self):
        another_app_template = Path(__file__).parent / "another_app_template"
        another_app_template.mkdir(exist_ok=True)
        assert another_app_template.is_dir()
        another_template_dir = (
            another_app_template / app_template_loader.loader.template_dirname
        )
        another_template_dir.mkdir(exist_ok=True)
        assert another_template_dir.is_dir()

        with self.mock_template_dir(
            app_dirs=[self.test_template_app, another_app_template]
        ):
            filename = "index.html"
            index_file = self._create_template_file(filename)
            index_file2 = self._create_template_file(
                filename, app_template=another_app_template
            )

            templates_found = [
                index_file.name,
                index_file2.name,
            ]
            assert templates_found == app_template_loader.list_templates()
            templates_found = [
                index_file,
                index_file2,
            ]
            with pytest.raises(ManyTemplateFoundError) as e:
                app_template_loader.get_template(filename)

            assert (
                f"Ambiguous template name, many templates found: {templates_found}"
                in str(e.value)
            )

            shutil.rmtree(str(another_app_template))
