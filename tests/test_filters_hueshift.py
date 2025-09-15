"""tests for the hueshift filter"""

# pylint: disable=missing-docstring

from . import lib

ORIG_COLORS = lib.make_colors(
    "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
)


class HueShiftTests(lib.FilterTestCase):
    entry_point = "hueshift"

    def test(self):
        config = lib.make_config("larry")

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#10608f #4fc7b1 #5c6283 #80305f #72ead3 #9f4b80 #e86e22 #85e934"
        )
        self.assertEqual(colors, expected)
