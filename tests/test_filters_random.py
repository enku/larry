"""tests for the random filter"""

# pylint: disable=missing-docstring,unused-argument

from unittest.mock import patch

from unittest_fixtures import Fixtures, given, where

from larry.filters.contrast import cfilter as contrast
from larry.filters.gradient import cfilter as gradient
from larry.filters.reduce import cfilter as reduce

from . import lib

ORIG_COLORS = lib.make_colors(
    "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
)


@given(lib.random)
@where(random__target="larry.filters.random.random")
class RandomTests(lib.FilterTestCase):
    entry_point = "random"

    def test(self, fixtures: Fixtures) -> None:
        config = lib.make_config("larry")

        with patch("larry.filters.contrast.cfilter", wraps=contrast) as cfilter:
            self.filter(ORIG_COLORS.copy(), config)

        cfilter.assert_called_with(ORIG_COLORS, config)

    def test_config_include(self, fixtures: Fixtures) -> None:
        config = lib.make_config("larry")
        config["filters:random"] = {"include": "gradient sepia"}

        with patch("larry.filters.gradient.cfilter", wraps=gradient) as cfilter:
            self.filter(ORIG_COLORS.copy(), config)

        cfilter.assert_called_with(ORIG_COLORS, config)

    def test_config_exclude(self, fixtures: Fixtures) -> None:
        config = lib.make_config("larry")
        config["filters:random"] = {"include": "-contrast -gradient"}

        with patch("larry.filters.reduce.cfilter", wraps=reduce) as cfilter:
            self.filter(ORIG_COLORS.copy(), config)

        cfilter.assert_called_once_with(ORIG_COLORS, config)
