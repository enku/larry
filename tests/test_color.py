# pylint: disable=missing-docstring
import random
from unittest import mock

from larry import color

from . import TestCase, make_colors

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

    def test_luminize(self):
        self.assertEqual(Color("#0e118f").luminize(70), Color("#2128ff"))

    def test_luminize_black(self):
        self.assertEqual(Color("#00000").luminize(70), Color("#464646"))

    def test_gradient(self):
        start, stop = make_colors("#000000 #ffffff")
        steps = 7

        colors = list(Color.gradient(start, stop, steps))

        expected = make_colors(
            "#000000 #2a2a2a #555555 #7f7f7f #aaaaaa #d4d4d4 #ffffff"
        )
        self.assertEqual(colors, expected)

    @mock.patch("larry.color.random", random.Random(1))
    def test_generate_from_with_same_number_of_colors(self):
        orig_colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        colors = list(Color.generate_from(orig_colors, len(orig_colors)))
        self.assertEqual(colors, orig_colors)

    def test_generate_from_with_negatative_needed(self):
        with self.assertRaises(ValueError):
            list(Color.generate_from([], -1))

    @mock.patch("larry.color.random", random.Random(1))
    def test_generate_from_when_no_colors_provided_yields_random_colors(self):
        colors = list(Color.generate_from([], 5))

        expected = make_colors("#442082 #3cfde6 #f1c26b #30f90e #c7dd01")
        self.assertEqual(colors, expected)

    @mock.patch("larry.color.random", random.Random(1))
    def test_generate_from_when_not_enough_colors(self):
        orig_colors = make_colors("#7e118f #754fc7 #835d75 #807930 #9772ea")

        colors = list(Color.generate_from(orig_colors, 7))

        expected = make_colors(
            "#754fc7 #835d75 #7e118f #807930 #87766e #8f74ac #9772ea"
        )
        self.assertEqual(colors, expected)

    @mock.patch("larry.color.random", random.Random(1))
    def test_generate_from_more_than_enough_colors(self):
        orig_colors = make_colors("#7e118f #754fc7 #835d75 #807930 #9772ea")

        colors = list(Color.generate_from(orig_colors, 3))

        expected = make_colors("#754fc7 #7e118f #9772ea")
        self.assertEqual(colors, expected)

    def test_generate_colors_when_2_input_colors_yields_gradient(self):
        orig_colors = make_colors("#807930 #7e118f")

        colors = list(Color.generate_from(orig_colors, 7))

        # gradient goes from input colors orderd by luminocity
        expected = make_colors(
            "#7e118f #7e227f #7e336f #7e445f #7f564f #7f673f #807930"
        )
        self.assertEqual(colors, expected)

    @mock.patch("larry.color.random", random.Random(1))
    def test_generate_from_when_needs_more_colors_than_input(self):
        orig_colors = make_colors("#7e118f #754fc7 #835d75 #7f564f")

        colors = list(Color.generate_from(orig_colors, 7))

        expected = make_colors(
            "#754fc7 #835d75 #7e118f #7f564f #823cfd #e6f1c2 #6b30f9"
        )
        self.assertEqual(colors, expected)

    @mock.patch("larry.color.random", random.Random(1))
    def test_randhue(self):
        s, v = 59, 86

        c = Color.randhue(s, v)

        h, s, v = c.to_hsv()
        self.assertEqual(round(h), 68)
        self.assertEqual(round(s), 59)
        self.assertEqual(round(v), 86)

    def test_to_hsv(self):
        h, s, v = Color("#9a59db").to_hsv()

        self.assertEqual(round(h), 270)
        self.assertEqual(round(s), 59)
        self.assertEqual(round(v), 86)

    def test_to_hsv_black(self):
        h, s, v = Color("#000000").to_hsv()

        self.assertEqual(round(h), 359)
        self.assertEqual(round(s), 0)
        self.assertEqual(round(v), 0)

    def test_from_hsv(self):
        hsv = (270, 59, 86)

        self.assertEqual(Color.from_hsv(hsv), Color("#9a59db"))

    def test_from_hsv_with_360(self):
        hsv = (360, 59, 86)

        self.assertEqual(Color.from_hsv(hsv), Color("#db5959"))

    def test_hsv_gray(self):
        hsv = (270, 0, 86)

        self.assertEqual(Color.from_hsv(hsv), Color("#dbdbdb"))


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
