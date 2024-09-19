# pylint: disable=missing-docstring
import tempfile
from pathlib import Path
from unittest import TestCase as StdlibTestCase

from larry import config
from larry.color import Color
from larry.config import DEFAULT_INPUT_PATH

RASTER_IMAGE = (Path(__file__).parent / "test.png").read_bytes()
SVG_IMAGE = Path(DEFAULT_INPUT_PATH).read_bytes()
CSS = """\
a {
  color: #4a4a4a;
  background: rgb(51,51,51);
}

b {
  color: #3a7e94;
  background: rgba(0, 45, 108, 0.6);
}

c {
  color: rgb(58, 126, 148);
  background: #002d6c;
}

d {
  color: #333;
}
"""


class TestCase(StdlibTestCase):
    def setUp(self):
        super().setUp()

        td = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(td.cleanup)
        self.tmpdir = td.name


class ConfigTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.config_path = f"{self.tmpdir}/larry.cfg"
        self._section = "larry"
        self.config = config.load(self.config_path)
        self.add_config(output=f"{self.tmpdir}/larry.svg")

    def add_config(self, **kwargs):
        for name, value in kwargs.items():
            self.config[self._section][name] = str(value)

        self._dump()

    def add_section(self, name: str):
        self.config.add_section(name)
        self._section = name
        self._dump()

    def _dump(self):
        with open(self.config_path, "w", encoding="UTF-8") as fp:
            self.config.write(fp)


def make_colors(colors: str) -> list[Color]:
    return [Color(s) for s in colors.split()]


def mock_write_file(bytes_io):
    def write_file(_filename: str, data: bytes):
        bytes_io.write(data)

    return write_file


def mock_write_text_file(bytes_io):
    def write_text_file(_filename: str, text: str, encoding: str = "utf8"):
        bytes_io.write(text.encode(encoding))

    return write_text_file
