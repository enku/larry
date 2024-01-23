# pylint: disable=missing-docstring
import tempfile
from unittest import TestCase as StdlibTestCase


class TestCase(StdlibTestCase):
    def setUp(self):
        super().setUp()

        td = tempfile.TemporaryDirectory()  # pylint: disable=consider-using-with
        self.addCleanup(td.cleanup)
        self.tmpdir = td.name
