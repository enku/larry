# pylint: disable=missing-docstring,unused-argument
from os import path
from unittest import TestCase

from unittest_fixtures import Fixtures, given

from larry import io

from . import lib


@given(lib.tmpdir)
class ReadFileTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        filename = path.join(fixtures.tmpdir, "test")
        with open(filename, "wb") as fp:
            fp.write(b"test")

        result = io.read_file(filename)

        self.assertEqual(result, b"test")

    def test_with_exclamation_runs_command(self, fixtures: Fixtures) -> None:
        filename = "!echo -n test"

        result = io.read_file(filename)

        self.assertEqual(result, b"test")


@given(lib.tmpdir)
class WriteFileTests(TestCase):
    def test(self, fixtures: Fixtures):
        filename = path.join(fixtures.tmpdir, "test")

        io.write_file(filename, b"test")

        with open(filename, "rb") as fp:
            result = fp.read()

        self.assertEqual(result, b"test")

    def test_with_exclamation_runs_command(self, fixtures: Fixtures) -> None:
        filename = path.join(fixtures.tmpdir, "test")

        io.write_file(f"!cat > {filename}", b"test")

        with open(filename, "rb") as fp:
            result = fp.read()

        self.assertEqual(result, b"test")
