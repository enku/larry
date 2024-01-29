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


def make_colors(colors: str) -> list[Color]:
    return [Color(s) for s in colors.split()]
