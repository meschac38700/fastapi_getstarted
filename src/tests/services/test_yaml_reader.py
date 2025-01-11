from pathlib import Path
from unittest import TestCase

from core.file_manager import YAMLReader


class TestYAMLReader(TestCase):
    def setUp(self):
        self.reader = YAMLReader(Path(__file__).parent / "data" / "heroes.yaml")

    def test_yaml_to_dict(self):
        expected = {
            "heroes": [
                {"name": "Captain America", "age": 43, "secret_name": "Chris Evans"},
                {"name": "Superman", "age": 41, "secret_name": "Clark Kent"},
                {"name": "Deadpool", "secret_name": "Ryan Reynolds"},
            ]
        }

        self.assertDictEqual(expected, self.reader.read())
