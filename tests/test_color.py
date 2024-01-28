# pylint: disable=missing-docstring
from larry import color

from . import TestCase

Color = color.Color
ColorFloat = color.ColorFloat

CSS = """\
a {
  color: #4a4a4a;
  background: rgb(51,51,51);
}

b {
  color: #3a7e94;
  background: rgba(0, 45, 108, 0.6);
}

c {
  color: rgb(58, 126, 148);
  background: #002d6c;
}

d {
  color: #333;
}
"""


class Betweeen0And1Tests(TestCase):
    def test_true(self):
        self.assertTrue(color.between_0_and_1(0.4))

    def test_false(self):
        self.assertFalse(color.between_0_and_1(-0.4))


class ColorReTests(TestCase):
    def test_can_find_colors(self):
        colors = color.COLORS_RE.findall(CSS)

        expected = [
            "#4a4a4a",
            "rgb(51,51,51)",
            "#3a7e94",
            "rgba(0, 45, 108, 0.6)",
            "rgb(58, 126, 148)",
            "#002d6c",
            "#333",
        ]
        self.assertEqual(colors, expected)


class ColorTests(TestCase):
    def test_is_gray(self):
        self.assertTrue(Color("#bfbfbf").is_gray())
        self.assertTrue(Color("#ffffff").is_gray())
        self.assertTrue(Color("#666666").is_gray())
        self.assertTrue(Color("#000000").is_gray())
        self.assertFalse(Color("red").is_gray())
        self.assertFalse(Color("#bfbfbd").is_gray())

    def test_is_gray_with_threshold(self):
        self.assertTrue(Color("#bfbfbd").is_gray(threshold=2))
        self.assertFalse(Color("#bfbfbd").is_gray(threshold=1))
        self.assertFalse(Color("#bfbebd").is_gray(threshold=1))

    def test_from_rgb_string(self):
        s = "rgb(100, 20, 30)"

        self.assertEqual(Color(s), Color(100, 20, 30))

    def test_from_rgba_string(self):
        s = "rgba(100, 20, 30, 0.4)"

        self.assertEqual(Color(s), Color(100, 20, 30))


class ClipTests(TestCase):
    def test1(self):
        self.assertEqual(color.clip(20), 20)

    def test2(self):
        self.assertEqual(color.clip(-20), 0)

    def test3(self):
        self.assertEqual(color.clip(20, maximum=19), 19)

    def test4(self):
        self.assertEqual(color.clip(-20, minimum=-4), -4)

    def test5(self):
        self.assertEqual(color.clip(300), 255)

    def test6(self):
        self.assertEqual(color.clip(-3), 0)


class ReplaceString(TestCase):
    def test1(self):
        colormap = {
            Color("#4a4a4a"): Color("#ffffff"),
            Color("#3a7e94"): Color("#000000"),
        }
        result = color.replace_string(CSS, colormap)
        expected = """\
a {
  color: #ffffff;
  background: rgb(51,51,51);
}

b {
  color: #000000;
  background: rgba(0, 45, 108, 0.6);
}

c {
  color: rgb(0, 0, 0);
  background: #002d6c;
}

d {
  color: #333;
}
"""
        self.assertEqual(result, expected)

    def test2(self):
        colormap = {
            Color("#333"): Color("#ffffff"),
        }
        result = color.replace_string(CSS, colormap)
        expected = """\
a {
  color: #4a4a4a;
  background: rgb(255, 255, 255);
}

b {
  color: #3a7e94;
  background: rgba(0, 45, 108, 0.6);
}

c {
  color: rgb(58, 126, 148);
  background: #002d6c;
}

d {
  color: #ffffff;
}
"""
        self.assertEqual(result, expected)

    def test3(self):
        colormap = {Color("#002d6c"): Color("#1245ef")}
        result = color.replace_string(CSS, colormap)
        expected = """\
a {
  color: #4a4a4a;
  background: rgb(51,51,51);
}

b {
  color: #3a7e94;
  background: rgba(18, 69, 239, 0.6);
}

c {
  color: rgb(58, 126, 148);
  background: #1245ef;
}

d {
  color: #333;
}
"""
        self.assertEqual(result, expected)


class ColorFloatTests(TestCase):
    def test_init_no_args(self):
        cf = ColorFloat()

        self.assertEqual(cf.red, 0)
        self.assertEqual(cf.green, 0)
        self.assertEqual(cf.blue, 0)
        self.assertEqual(cf.alpha, 1)

    def test_init_with_values(self):
        cf = ColorFloat(red=0.4, green=0.5, blue=0.6, alpha=0.7)

        self.assertEqual(cf.red, 0.4)
        self.assertEqual(cf.green, 0.5)
        self.assertEqual(cf.blue, 0.6)
        self.assertEqual(cf.alpha, 0.7)

    def test_init_with_invalid_value(self):
        with self.assertRaises(ValueError):
            ColorFloat(alpha=1.4)

    def test_from_color(self):
        testcolor = Color(103, 95, 148)
        alpha = 0.7

        cf = ColorFloat.from_color(testcolor, alpha)

        self.assertEqual(cf.red, 103 / 255)
        self.assertEqual(cf.green, 95 / 255)
        self.assertEqual(cf.blue, 148 / 255)
        self.assertEqual(cf.alpha, 0.7)

    def test_to_color(self):
        cf = ColorFloat(red=103 / 255, green=95 / 255, blue=148 / 255, alpha=0.7)
        self.assertEqual(cf.to_color(), Color("#675f94"))


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
