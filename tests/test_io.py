# pylint: disable=missing-docstring
from os import path

from larry import io

from . import TestCase


class ReadFileTests(TestCase):
    def test(self):
        filename = path.join(self.tmpdir, "test")
        with open(filename, "wb") as fp:
            fp.write(b"test")

        result = io.read_file(filename)

        self.assertEqual(result, b"test")

    def test_with_exclamation_runs_command(self):
        filename = "!echo -n test"

        result = io.read_file(filename)

        self.assertEqual(result, b"test")


class WriteFileTests(TestCase):
    def test(self):
        filename = path.join(self.tmpdir, "test")

        io.write_file(filename, b"test")

        with open(filename, "rb") as fp:
            result = fp.read()

        self.assertEqual(result, b"test")

    def test_with_exclamation_runs_command(self):
        filename = path.join(self.tmpdir, "test")

        io.write_file(f"!cat > {filename}", b"test")

        with open(filename, "rb") as fp:
            result = fp.read()

        self.assertEqual(result, b"test")
