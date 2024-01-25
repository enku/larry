# pylint: disable=missing-docstring
import tempfile
from unittest import TestCase as StdlibTestCase

from larry.color import Color


class TestCase(StdlibTestCase):
    def setUp(self):
        super().setUp()

        td = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(td.cleanup)
        self.tmpdir = td.name


def make_colors(colors: str) -> list[Color]:
    return [Color(s) for s in colors.split()]
