import logging
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from core.commands.cli import app as main_app
from settings import settings as app_settings
from settings.app import Settings


class MockSettings(Settings):
    APPS_ROOT: Path = Path(__file__).parent / "data" / "collectstatics"

    @property
    def static_path(self):
        return self.apps_folder / app_settings.STATIC_ROOT

    @property
    def apps_folder(self):
        return self.APPS_ROOT


APP1 = "bar"
APP2 = "foo"


@pytest.fixture
def app_tree():
    """Create an application tree scenario for testing purposes.

    data
      collectstatics (apps folder)
        bar (app)
          statics
            test.css
        foo (app)
    """
    from core.services.runners import collect_statics

    with patch.object(collect_statics, "settings", MockSettings()) as mock_settings:
        from core.services.files import apps

        with patch.object(apps, "settings", MockSettings()) as _:
            app_root = mock_settings.static_path.parent

            # global statics folder
            mock_settings.static_path.mkdir(parents=True, exist_ok=True)

            # BAR application
            bar = app_root / APP1 / mock_settings.STATIC_ROOT
            bar.mkdir(parents=True, exist_ok=True)
            (bar / "test.css").touch(exist_ok=True)  # create a static file

            # second app FOO
            foo = app_root / APP2
            foo.mkdir(parents=True, exist_ok=True)

            yield app_root
            shutil.rmtree(mock_settings.apps_folder)


@pytest.mark.usefixtures("app_tree")
def test_collect_staticfiles_from_specific_app(cli_runner, caplog):
    caplog.set_level(logging.INFO)

    result = cli_runner.invoke(main_app, ["collectstatic", "-a", APP2, "-a", APP1])

    assert result.exit_code == 0
    assert "Collecting static files..." in caplog.text
    assert f"Skipping app '{APP2}' as no static module found." in caplog.text
    assert (
        f"Prepare to collect staticfiles from: ['tests.core.commands.data.collectstatics.{APP1}.statics']"
        in caplog.text
    )
    assert (
        f"1 Staticfiles collected from: tests/core/commands/data/collectstatics/{APP1}/statics/test.css"
        in caplog.text
    )


def test_clear_and_collect_staticfiles(app_tree, cli_runner, caplog, settings):
    caplog.set_level(logging.INFO)

    # Fill the destination folder before collection
    files_to_clear = ["subfile.css", "file1.css", "file2.js"]
    subfolder = app_tree / settings.STATIC_ROOT / "subfolder"
    subfolder.mkdir(parents=True, exist_ok=True)
    (subfolder / "subfile.css").touch(exist_ok=True)

    static_folder = app_tree / settings.STATIC_ROOT
    # hidden file
    hidden_file = static_folder / ".hidden.txt"
    hidden_file.touch(exist_ok=True)
    for file_to_clear in files_to_clear[1:]:
        (app_tree / settings.STATIC_ROOT / file_to_clear).touch(exist_ok=True)

    result = cli_runner.invoke(main_app, ["collectstatic", "-c"])

    assert result.exit_code == 0
    assert "Collecting static files..." in caplog.text
    assert f"{len(files_to_clear)} staticfiles cleared." in caplog.text
    assert (
        f"1 Staticfiles collected from: tests/core/commands/data/collectstatics/{APP1}/statics/test.css"
        in caplog.text
    )
    assert hidden_file.exists()


def test_collect_staticfiles_no_file_to_collect(app_tree, cli_runner, caplog):
    caplog.set_level(logging.INFO)

    # empty apps folder
    shutil.rmtree(app_tree, ignore_errors=True)
    app_tree.mkdir(parents=True, exist_ok=True)

    result = cli_runner.invoke(main_app, ["collectstatic"])

    assert result.exit_code == 0
    assert "Collecting static files..." in caplog.text
    assert "No static files were found to be collected" in caplog.text
