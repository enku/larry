"""Tests for the sine filter"""

# pylint: disable=missing-docstring


import contextlib as context
import io

from unittest_fixtures import Fixtures, given, where

from . import lib

ORIG_COLORS = lib.make_colors(
    "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
)


@given(lib.configmaker)
@given(lib.random)
@where(random__target="larry.filters.sine.random", random__seed=7000)
class SineTests(lib.FilterTestCase):
    entry_point = "sine"

    def test(self, fixtures: Fixtures) -> None:
        config = fixtures.configmaker.config

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#09010a #020103 #32232d #e8db57 #030204 #ffff85 #6dff41 #31d2db"
        )
        self.assertEqual(colors, expected)

    def test_cosine(self, fixtures: Fixtures) -> None:
        config = fixtures.configmaker.config
        config["filters:sine"] = {"mode": "cosine"}

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#ad17c4 #5e3fa1 #eaa6d1 #c9be4b #785bbb #ffee79 #228d14 #000000"
        )
        self.assertEqual(colors, expected)

    def test_random(self, fixtures: Fixtures) -> None:
        config = fixtures.configmaker.config
        config["filters:sine"] = {"mode": "random"}

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#ad17c4 #020103 #eaa6d1 #e8db57 #785bbb #ffff85 #6dff41 #000000"
        )
        self.assertEqual(colors, expected)

    def test_invalid_mode(self, fixtures: Fixtures) -> None:
        config = fixtures.configmaker.config
        config["filters:sine"] = {"mode": "bogus"}
        stderr = io.StringIO()

        with context.redirect_stderr(stderr):
            colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#09010a #020103 #32232d #e8db57 #030204 #ffff85 #6dff41 #31d2db"
        )
        self.assertEqual(colors, expected)
        self.assertTrue(stderr.getvalue())
