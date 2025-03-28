import glob
import logging
from collections.abc import Iterable, Sequence
from pathlib import Path

import settings
from core.db import SQLTable
from core.db.fixtures import utils as fixture_utils
from core.db.fixtures.files import FixtureFileReader

_APP_DIR = settings.BASE_DIR / "apps"
_logger = logging.getLogger(__name__)


class LoadFixtures:
    _ALLOWED_FILES = [".yaml", ".yml"]

    def __init__(
        self, app_dir: str | Path = _APP_DIR, *, logger: logging.Logger | None = None
    ):
        self.app_dir: Path = Path(app_dir)
        self.logger = logger or _logger
        self.count_created = 0

    async def _extract_models(self, file_path: Path):
        """Extract model instances from the given yaml file path."""
        fixture_file_reader = FixtureFileReader(file_path=file_path)
        return [model async for model in await fixture_file_reader.models()]

    async def _load_fixtures(self, fixture_files: Iterable[str]) -> int:
        count = 0
        for fixture_file in fixture_files:
            fixture_file_path = Path(fixture_file)

            models = await self._extract_models(fixture_file_path)
            await SQLTable.objects().insert_batch(models)
            count += len(models)

        return count

    def _get_app_paths(self):
        """Scan apps dir to extract all application pathname."""
        return (
            potential_app
            for potential_app in glob.glob(str(self.app_dir / "*"))
            if (Path(potential_app) / "models").exists()
            or (Path(potential_app) / "models.py").exists()
        )

    def _scan_fixture_files(self, app: Path):
        """Scan the given app path to extract all fixtures paths."""
        fixture_files = []
        for ext in self._ALLOWED_FILES:
            pattern = app / "fixtures" / "**" / f"*{ext}"
            fixture_files.extend(glob.glob(str(pattern), recursive=True))

        return fixture_files

    async def _load_app_fixtures(self, fixtures_files: Iterable[str], app_name: str):
        self.logger.info(f"Loading {app_name} fixtures.")
        count = await self._load_fixtures(fixtures_files)
        self.logger.info(
            f"Loaded a total of {count} fixtures for the {app_name} application."
        )
        self.count_created += count

    def _extract_app_name(self, fixture_path: Path):
        """Extract app name from the given fixture path."""
        try:
            return (
                str(fixture_path)
                .replace(str(self.app_dir), "")
                .lstrip("/")
                .split("/")[0]
            )
        except IndexError:
            return None

    def _filter_fixture_files(
        self, fixture_files: Sequence[str], desired_fixture_names: Sequence[str]
    ) -> Iterable[str]:
        self.logger.info(f"Processing {len(desired_fixture_names)} fixture files.")
        return (
            fixture_file
            for fixture_file in fixture_files
            if Path(fixture_file).stem in desired_fixture_names
            or Path(fixture_file).name in desired_fixture_names
        )

    async def _load_fixtures_by_name(
        self, fixture_names: Sequence[str] | None = None
    ) -> int:
        """Load ths given fixtures names or default one from initial_fixtures.

        example:
         > self.load_fixtures() # load all specified initial fixtures from settings initial_fixtures
         > self.load_fixtures(['initial_users']) # load the provided fixtures
        """
        _fixture_names = fixture_names or settings.initial_fixtures
        for app in fixture_utils.preserve_fixtures_order(
            self._get_app_paths(), _fixture_names
        ):
            _app = Path(app)
            fixtures_files = self._scan_fixture_files(_app)

            app_name = _app.stem.title()
            fixtures_files = self._filter_fixture_files(fixtures_files, _fixture_names)
            await self._load_app_fixtures(fixtures_files, app_name)

        self.logger.info(f"Total of {self.count_created} fixtures loaded.")
        return self.count_created

    async def _load_fixtures_by_path(self, fixture_paths: Sequence[Path | str]) -> int:
        """Load the given fixture paths."""
        for fixture_path in fixture_paths:
            _fixture_path = Path(fixture_path).absolute()
            # get app name
            app_name = self._extract_app_name(_fixture_path)
            if app_name is None:
                self.logger.info(
                    f"Invalid fixture file: {fixture_path}. Could not retrieve the app name."
                )
                continue

            await self._load_app_fixtures([str(_fixture_path)], app_name)

        return self.count_created

    async def load_fixtures(
        self, fixtures: Sequence[str | Path] | None = None, is_path: bool = False
    ):
        if is_path:
            return await self._load_fixtures_by_path(fixtures)

        return await self._load_fixtures_by_name(fixtures)
