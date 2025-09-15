"""tests for the hueshift filter"""

# pylint: disable=missing-docstring,unused-argument

import io
from contextlib import redirect_stderr

from unittest_fixtures import Fixtures, given, where

from . import lib

ORIG_COLORS = lib.make_colors(
    "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
)


@given(lib.random)
@where(random__target="larry.filters.hueshift.random")
@given(stderr=lambda _: redirect_stderr(io.StringIO()))
class HueShiftTests(lib.FilterTestCase):
    entry_point = "hueshift"

    def test(self, fixtures: Fixtures) -> None:
        config = lib.make_config("larry")

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#10608f #4fc7b1 #5c6283 #80305f #72ead3 #9f4b80 #e86e22 #85e934"
        )
        self.assertEqual(colors, expected)

    def test_random_amount(self, fixtures: Fixtures) -> None:
        config = lib.make_config("larry")
        config["filters:hueshift"] = {"amount": "random"}

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#8f103a #c74fb8 #83635c #468030 #ea72dc #679f4b #22e8aa #344de9"
        )
        self.assertEqual(colors, expected)

    def test_invalid_amount_given(self, fixtures: Fixtures) -> None:
        config = lib.make_config("larry")
        config["filters:hueshift"] = {"amount": "bogus"}

        with fixtures.stderr as stderr:
            colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#10608f #4fc7b1 #5c6283 #80305f #72ead3 #9f4b80 #e86e22 #85e934"
        )
        self.assertEqual(colors, expected)
        self.assertEqual(
            stderr.getvalue(), "amount could not be parsed as float: bogus\n"
        )
