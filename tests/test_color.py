# pylint: disable=missing-docstring
from larry import color

from . import TestCase

Color = color.Color
ColorFloat = color.ColorFloat


class RGBATests(TestCase):
    def test(self):
        color_str = "255, 0, 0, 0.76"
        c = Color("#0000ff")
        string = "rgba(0, 0, 255, 0.76); rgba(255, 0, 0, 0.76) test"

        result = color.rgba(color_str, c, string)

        self.assertEqual(result, "rgba(0, 0, 255, 0.76); rgba(0, 0, 255, 0.76) test")


class CombineTests(TestCase):
    def test(self):
        fg = ColorFloat.from_color(Color("#0000ff"), 0.6)
        bg = ColorFloat.from_color(Color("#ff0000"), 0.4)

        # #3500c9, alpha 0.76
        combined = color.combine(fg, bg)

        self.assertAlmostEqual(combined.red, 0.21052631578947373)
        self.assertAlmostEqual(combined.green, 0.0)
        self.assertAlmostEqual(combined.blue, 0.7894736842105263)
        self.assertEqual(combined.alpha, 0.76)

    def test_almost_clear(self):
        fg = ColorFloat.from_color(Color("#0000ff"), 0.0000001)
        bg = ColorFloat.from_color(Color("#ff0000"), 0.0000001)

        # #000000, alpha 0
        combined = color.combine(fg, bg)

        self.assertAlmostEqual(combined.red, 0.0)
        self.assertAlmostEqual(combined.green, 0.0)
        self.assertAlmostEqual(combined.blue, 0.0)
        self.assertEqual(combined.alpha, 0)


class CombineColorsTests(TestCase):
    def test(self):
        fg = Color("#0000ff")
        bg = Color("#ff0000")
        opacity = 0.6

        c = color.combine_colors(fg, bg, opacity)
        self.assertEqual(c, Color("#660099"))

        opacity = 0.4
        c = color.combine_colors(fg, bg, opacity)
        self.assertEqual(c, Color("#990066"))
