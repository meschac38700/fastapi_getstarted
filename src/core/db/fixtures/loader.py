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
        return await fixture_file_reader.models()

    async def _load_fixtures(self, fixture_files: Iterable[str]) -> int:
        count = 0
        for fixture_file in fixture_files:
            fixture_file_path = Path(fixture_file)

            models = list(await self._extract_models(fixture_file_path))
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

    async def load_fixtures(self, fixture_names: Sequence[str] | None = None) -> int:
        _fixture_names = fixture_names or settings.initial_fixtures
        for app in fixture_utils.preserve_fixtures_order(
            self._get_app_paths(), _fixture_names
        ):
            _app = Path(app)
            fixtures_files = self._scan_fixture_files(_app)

            app_name = _app.stem.title()
            self.logger.info(f"Loading {app_name} fixtures.")
            count = await self._load_fixtures(
                self._filter_fixture_files(fixtures_files, _fixture_names)
            )
            self.logger.info(f"Loaded a total of {count} {app_name} elements.")
            self.count_created += count

        self.logger.info(f"Total of {self.count_created} fixtures loaded.")
        return self.count_created

    def _filter_fixture_files(
        self, fixture_files: Sequence[str], desired_fixture_names: Sequence[str]
    ) -> Iterable[str]:
        if not desired_fixture_names or not isinstance(desired_fixture_names, Iterable):
            desired_fixture_names = settings.initial_fixtures

        self.logger.info(f"Processing {len(desired_fixture_names)} fixture files.")
        return (
            fixture_file
            for fixture_file in fixture_files
            if Path(fixture_file).stem in desired_fixture_names
            or Path(fixture_file).name in desired_fixture_names
        )
