# pylint: disable=missing-docstring
import tempfile
from pathlib import Path
from unittest import TestCase as StdlibTestCase

from larry.color import Color
from larry.config import DEFAULT_INPUT_PATH

RASTER_IMAGE = (Path(__file__).parent / "test.png").read_bytes()
SVG_IMAGE = Path(DEFAULT_INPUT_PATH).read_bytes()


class TestCase(StdlibTestCase):
    def setUp(self):
        super().setUp()

        td = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(td.cleanup)
        self.tmpdir = td.name


class ConfigTestCase(TestCase):
    def setUp(self):
        super().setUp()

        # TODO: use actual ConfigParser for this
        config = f"""\
[larry]
output = {self.tmpdir}/larry.svg
"""
        self.config_path = f"{self.tmpdir}/larry.cfg"
        with open(self.config_path, "w", encoding="UTF-8") as fp:
            fp.write(config)

    def add_config(self, **kwargs):
        with self._append() as config_file:
            for name, value in kwargs.items():
                print(f"{name} = {value}", file=config_file)

    def add_section(self, name: str):
        with self._append() as config_file:
            print("", file=config_file)
            print(f"[{name}]", file=config_file)

    def _append(self):
        return open(self.config_path, "a", encoding="UTF-8")


def make_colors(colors: str) -> list[Color]:
    return [Color(s) for s in colors.split()]
