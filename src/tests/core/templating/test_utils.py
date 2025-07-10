import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from core.templating.loaders import app_template_loader
from core.templating.utils import render


@pytest.fixture
def app_dir():
    return Path(__file__).parent


@pytest.fixture
def template_dir(app_dir: Path) -> Path:
    template_dir = app_dir / app_template_loader.loader.template_dirname
    template_dir.mkdir(parents=True, exist_ok=True)
    return template_dir


def test_get_render_template(app_dir: Path, template_dir: Path):
    with patch("core.templating.loaders.apps.file_services") as mock_file_services:
        mock_file_services.get_application_paths.return_value = [app_dir]
        index_file = template_dir / "index.html"

        expected_text = "<h1>render template: {{template_name}}</h1>"
        index_file.write_text(expected_text)

        template_content = render(
            index_file.name, context={"template_name": index_file.name}
        )

        assert template_content == expected_text.replace(
            "{{template_name}}", index_file.name
        )
        # clear test data
        shutil.rmtree(str(template_dir), ignore_errors=True)
