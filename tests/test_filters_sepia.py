"""Tests for the sepia filter"""

# pylint: disable=missing-docstring
import io
from contextlib import redirect_stderr

from unittest_fixtures import Fixtures, given, where

from . import lib

ORIG_COLORS = lib.make_colors(
    "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
)


@given(lib.random, lib.configmaker)
@where(random__target="larry.filters.sepia.random")
class SepiaTests(lib.FilterTestCase):
    entry_point = "sepia"

    def test(self, fixtures: Fixtures) -> None:
        config = fixtures.configmaker.config

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#564730 #837e4d #827e44 #84873f #aca863 #a5a851 #a9c756 #c8e179"
        )
        self.assertEqual(colors, expected)

    def test_random_config(self, fixtures: Fixtures) -> None:
        config = fixtures.configmaker.config
        config["filters:sepia"] = {
            "red_multiplier": "random",
            "green_base": "random",
            "blue_adjustment": "random",
        }

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#4e4880 #5e8497 #568697 #4b9190 #76b0c3 #60b4b5 #3bd97a #5ef29a"
        )
        self.assertEqual(colors, expected)

    def test_invalid_config(self, fixtures: Fixtures) -> None:
        config = fixtures.configmaker.config
        config["filters:sepia"] = {"blue_adjustment": "notanumber"}
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            colors = self.filter(ORIG_COLORS, config)

        self.assertEqual(
            stderr.getvalue(), 'blue_adjustment: "notanumber" is not a valid number\n'
        )

        expected = lib.make_colors(
            "#564730 #837e4d #827e44 #84873f #aca863 #a5a851 #a9c756 #c8e179"
        )
        self.assertEqual(colors, expected)
