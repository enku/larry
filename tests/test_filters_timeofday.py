"""Tests for the timeofday filter"""

# pylint: disable=missing-docstring
import datetime as dt
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, params

from larry.filters import timeofday

from . import lib

ORIG_COLORS = lib.make_colors(
    "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
)


@params(time=["06:00:00", "9:00:00", "14:00:00", "18:00:00", "20:30:00", "22:00:00"])
@params(
    expected=[
        "#640d72 #5d3f9f #684a5d #666026 #785bbb #7f753c #2db91b #2ab2ba",
        "#710f80 #6947b3 #755369 #736c2b #8766d2 #8f8443 #33d01e #2fc8d1",
        "#7e108f #754fc7 #835c75 #807830 #9772ea #9f934b #39e822 #34dfe9",
        "#7e108f #754fc7 #835c75 #807830 #9772ea #9f934b #39e822 #34dfe9",
        "#5c0c68 #553991 #604455 #5d5823 #6e53ab #746b37 #29aa18 #26a3aa",
        "#3f0847 #3a2763 #412e3a #403c18 #4b3975 #4f4925 #1c7411 #1a6f74",
    ]
)
class TimeOfDayFilters(lib.FilterTestCase):
    entry_point = "timeofday"

    def test(self, fixtures: Fixtures) -> None:
        config = lib.make_config("larry")
        hour, minute, second = (int(s) for s in fixtures.time.split(":"))

        with mock.patch("larry.filters.timeofday.now") as now:
            now.return_value = dt.datetime(2025, 9, 7, hour, minute, second)
            colors = self.filter(ORIG_COLORS, config)

        self.assertEqual(
            colors, lib.make_colors(fixtures.expected), " ".join(str(c) for c in colors)
        )


class TimeOfDayFilterConfigurableDaystart(lib.FilterTestCase):
    entry_point = "timeofday"

    def test(self) -> None:
        config = lib.make_config("larry")
        config.add_section("filters:timeofday")
        config.set("filters:timeofday", "midday", "9")

        with mock.patch("larry.filters.timeofday.now") as now:
            now.return_value = dt.datetime(2025, 9, 7, 9, 0, 0)
            colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#7e108f #754fc7 #835c75 #807830 #9772ea #9f934b #39e822 #34dfe9"
        )
        self.assertEqual(colors, expected)


class ParseRangeTests(TestCase):
    def test(self) -> None:
        self.assertEqual(timeofday.parse_range("0.72-6.4"), (0.72, 6.4))

    def test_missing_parts(self) -> None:
        self.assertEqual(timeofday.parse_range("0.72"), None)
