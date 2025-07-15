from pathlib import Path

from core.services.files import YAMLReader
from core.unittest.async_case import AsyncTestCase


class TestYAMLReader(AsyncTestCase):
    def test_yaml_to_dict(self):
        self.reader = YAMLReader(Path(__file__).parent / "data" / "heroes.yaml")
        expected = {
            "heroes": [
                {"name": "Captain America", "age": 43, "secret_name": "Chris Evans"},
                {"name": "Superman", "age": 41, "secret_name": "Clark Kent"},
                {"name": "Deadpool", "secret_name": "Ryan Reynolds"},
            ]
        }

        assert expected == self.reader.read()
