# pylint: disable=missing-docstring,duplicate-code,unused-argument
from unittest import TestCase

import numpy as np
from unittest_fixtures import Fixtures, given

from larry import color

from . import lib

Color = color.Color
ColorFloat = color.ColorFloat


class ColorReTests(TestCase):
    def test_can_find_colors(self):
        colors = color.COLORS_RE.findall(lib.CSS)

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


@given(lib.random)
class ColorTests(TestCase):  # pylint: disable=too-many-public-methods
    def test_is_gray(self, fixtures: Fixtures) -> None:
        self.assertTrue(Color("#bfbfbf").is_gray())
        self.assertTrue(Color("#ffffff").is_gray())
        self.assertTrue(Color("#666666").is_gray())
        self.assertTrue(Color("#000000").is_gray())
        self.assertFalse(Color("red").is_gray())
        self.assertFalse(Color("#bfbfbd").is_gray())

    def test_is_gray_with_threshold(self, fixtures: Fixtures) -> None:
        self.assertTrue(Color("#bfbfbd").is_gray(threshold=2))
        self.assertFalse(Color("#bfbfbd").is_gray(threshold=1))
        self.assertFalse(Color("#bfbebd").is_gray(threshold=1))

    def test_init_with_no_args_is_random(self, fixtures: Fixtures) -> None:
        c = Color()

        self.assertEqual(c, Color("#442082"))

    def test_init_values_out_of_range(self, fixtures: Fixtures) -> None:
        with self.assertRaises(ValueError):
            Color(255, 255, 300)

    def test_init_from_wrong_number_of_args(self, fixtures: Fixtures) -> None:
        with self.assertRaises(color.BadColorSpecError):
            Color(255, 255)

    def test_init_from_color(self, fixtures: Fixtures) -> None:
        c = Color("#3249ab")

        self.assertEqual(Color(c), c)

    def test_init_bad_colorspec(self, fixtures: Fixtures) -> None:
        with self.assertRaises(color.BadColorSpecError):
            Color(None)

    def test_from_rgb_string(self, fixtures: Fixtures) -> None:
        s = "rgb(100, 20, 30)"

        self.assertEqual(Color(s), Color(100, 20, 30))

    def test_from_rgba_string(self, fixtures: Fixtures) -> None:
        s = "rgba(100, 20, 30, 0.4)"

        self.assertEqual(Color(s), Color(100, 20, 30))

    def test_init_from_random(self, fixtures: Fixtures) -> None:
        c = Color("random")

        self.assertEqual(c, Color("#442082"))

    def test_init_string_slashes(self, fixtures: Fixtures) -> None:
        c = Color("100/20/30")

        self.assertEqual(c, Color(100, 20, 30))

    def test_init_string_braces(self, fixtures: Fixtures) -> None:
        c = Color("{1.0, 0.2, 0.3}")

        self.assertEqual(c, Color(255, 51, 76))

    def test_init_random_with_lum(self, fixtures: Fixtures) -> None:
        c = Color("random(34)")

        self.assertEqual(c, Color("#2b1452"))
        self.assertEqual(round(c.luminocity()), 34)

    def test_init_random_with_lum_gt(self, fixtures: Fixtures) -> None:
        c = Color("random(>34)")

        self.assertEqual(c, Color("#52279c"))
        self.assertGreater(round(c.luminocity()), 34)

    def test_init_random_with_lum_gte(self, fixtures: Fixtures) -> None:
        c = Color("random(>=34)")

        self.assertEqual(c, Color("#51269a"))
        self.assertGreaterEqual(round(c.luminocity()), 34)

    def test_init_random_with_lum_error(self, fixtures: Fixtures) -> None:
        with self.assertRaises(color.BadColorSpecError):
            Color("random(==34)")

    def test_init_from_randhue(self, fixtures: Fixtures) -> None:
        c = Color("randhue(50, 20)")

        self.assertEqual(c, Color("#2f3319"))
        _, s, v = c.to_hsv()
        self.assertEqual(int(s), 50)
        self.assertEqual(int(v), 20)

    def test_from_rrggbb_string(self, fixtures: Fixtures) -> None:
        c = Color(50, 73, 171)

        self.assertEqual(Color("#3249ab"), c)
        self.assertEqual(Color("3249ab"), c)

        self.assertEqual(Color("#cab"), Color("#ccaabb"))
        self.assertEqual(Color("cab"), Color("#ccaabb"))

    def test_bad_init_string_raises_error(self, fixtures: Fixtures) -> None:
        with self.assertRaises(color.BadColorSpecError):
            Color("bogus")

    def test_add_float(self, fixtures: Fixtures) -> None:
        c1 = Color("#3249ab")
        c2 = c1 + 20.0

        self.assertEqual(c2, Color("#465dbf"))

    def test_add_color(self, fixtures: Fixtures) -> None:
        c1 = Color("#3249ab")
        c2 = Color("#040404")
        c3 = c1 + c2

        self.assertEqual(c3, Color("#364daf"))

    def test_mul_float(self, fixtures: Fixtures) -> None:
        c1 = Color("#3249ab")
        c2 = c1 * 0.3

        self.assertEqual(c2, Color("#0f1533"))

        c2 = c1 * 1.3

        self.assertEqual(c2, Color("#415ede"))

    def test_mul_color(self, fixtures: Fixtures) -> None:
        # I don't particularly see the point in this. Maybe remove
        c1 = Color("#3249ab")
        c2 = Color("#040404")
        c3 = c1 * c2

        self.assertEqual(c3, Color("#c8ffff"))

    def test_sub(self, fixtures: Fixtures) -> None:
        c1 = Color("#ffa500")
        c2 = Color("#3249ab")
        c3 = c1 - c2

        self.assertEqual(c3, Color("#cd5c00"))

    def test_colorify(self, fixtures: Fixtures) -> None:
        c1 = Color("#3249ab")
        c2 = Color("#ffa500")
        c3 = c1.colorify(c2)

        self.assertEqual(c3, Color("#aa8031"))

    def test_colorify_fix_bw(self, fixtures: Fixtures) -> None:
        c1 = Color("#ffffff")
        c2 = Color("#ffa500")
        c3 = c1.colorify(c2, fix_bw=True)

        self.assertEqual(c3, Color("#fefefe"))

        c1 = Color("#000000")
        c3 = c1.colorify(c2, fix_bw=True)

        self.assertEqual(c3, Color("#010101"))

    def test_randcolor(self, fixtures: Fixtures) -> None:
        self.assertEqual(Color.randcolor(), Color("#442082"))

    def test_randcolor_with_lum(self, fixtures: Fixtures) -> None:
        c = Color.randcolor(lum=34)
        self.assertEqual(c, Color("#2b1452"))
        self.assertEqual(round(c.luminocity()), 34)

        c = Color.randcolor(lum=34, comp="<")
        self.assertEqual(c, Color("#092724"))
        self.assertLess(c.luminocity(), 34)

        c = Color.randcolor(lum=34, comp="<=")
        self.assertEqual(c, Color("#2f1a0c"))
        self.assertLessEqual(c.luminocity(), 34)

        c = Color.randcolor(lum=34, comp=">")
        self.assertEqual(c, Color("#12ffff"))
        self.assertGreater(c.luminocity(), 34)

        c = Color.randcolor(lum=34, comp=">=")
        self.assertEqual(c, Color("#01ffc6"))
        self.assertGreaterEqual(c.luminocity(), 34)

        with self.assertRaises(color.BadColorSpecError):
            Color.randcolor(lum=34, comp="lt")

    def test_inverse(self, fixtures: Fixtures) -> None:
        c = Color("#3249ab")
        inverse = c.inverse()

        self.assertEqual(inverse, Color("#cdb654"))

    def test_winverse(self, fixtures: Fixtures) -> None:
        c = Color("#3249ab")
        winverse = c.winverse()

        self.assertEqual(winverse, Color("#19b600"))

    def test_to_gtk(self, fixtures: Fixtures) -> None:
        c = Color("#3249ab")

        self.assertEqual(c.to_gtk(), "0.20, 0.29, 0.67")

    def test_to_ansi256(self, fixtures: Fixtures) -> None:
        c = Color("#3249ab")

        self.assertEqual(c.to_ansi256(), 61)

    def test_to_ansi256_gray(self, fixtures: Fixtures) -> None:
        self.assertEqual(Color("#acacac").to_ansi256(), 248)
        self.assertEqual(Color("#000000").to_ansi256(), 16)
        self.assertEqual(Color("#ffffff").to_ansi256(), 231)

    def test_pastelize(self, fixtures: Fixtures) -> None:
        c = Color("#3249ab")
        p = Color("#7f97ff")

        self.assertEqual(c.pastelize(), p)

        h, s, v = p.to_hsv()
        self.assertEqual(round(h), round(c.to_hsv()[0]))
        self.assertEqual(round(s), color.PASTEL_SATURATION)
        self.assertEqual(round(v), color.PASTEL_BRIGHTNESS)

    def test_pastelize_custom(self, fixtures: Fixtures) -> None:
        c = Color("#3249ab")
        s = 134
        v = 90
        p = c.pastelize(saturation=s, brightness=v)

        self.assertEqual(p, Color("#0000e5"))
        self.assertEqual(p, Color.from_hsv((c.to_hsv()[0], s, v)))

    def test_luminize(self, fixtures: Fixtures) -> None:
        self.assertEqual(Color("#0e118f").luminize(70), Color("#2128ff"))

    def test_luminize_black(self, fixtures: Fixtures) -> None:
        self.assertEqual(Color("#000000").luminize(70), Color("#464646"))

    def test_gradient(self, fixtures: Fixtures) -> None:
        start, stop = lib.make_colors("#000000 #ffffff")
        steps = 7

        colors = list(Color.gradient(start, stop, steps))

        expected = lib.make_colors(
            "#000000 #242424 #484848 #6d6d6d #919191 #b6b6b6 #ffffff"
        )
        self.assertEqual(colors, expected)

    def test_get_gradient_color(self, fixtures: Fixtures) -> None:
        orig_colors = lib.make_colors("#ff0000 #00ff00 #0000ff")

        colors = list(color.get_gradient_color(orig_colors, 7, i) for i in range(7))

        expected = lib.make_colors(
            "#ff0000 #bf3f00 #7f7f00 #00ff00 #00bf3f #007f7f #0000ff"
        )
        self.assertEqual(colors, expected, " ".join(str(i) for i in colors))

    def test_generate_from_with_same_number_of_colors(self, fixtures: Fixtures) -> None:
        orig_colors = lib.make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        colors = list(Color.generate_from(orig_colors, len(orig_colors)))
        self.assertEqual(colors, orig_colors)

    def test_generate_from_with_negatative_needed(self, fixtures: Fixtures) -> None:
        with self.assertRaises(ValueError):
            list(Color.generate_from([], -1))

    def test_generate_from_when_no_colors_provided_yields_random_colors(
        self, fixtures: Fixtures
    ) -> None:
        colors = list(Color.generate_from([], 5))

        expected = lib.make_colors("#442082 #3cfde6 #f1c26b #30f90e #c7dd01")
        self.assertEqual(colors, expected)

    def test_generate_from_when_not_enough_colors(self, fixtures: Fixtures) -> None:
        orig_colors = lib.make_colors("#7e118f #754fc7 #835d75 #807930 #9772ea")

        colors = list(Color.generate_from(orig_colors, 7))

        expected = lib.make_colors(
            "#754fc7 #835d75 #7e118f #807930 #85765e #8b758d #9772ea"
        )
        self.assertEqual(colors, expected)

    def test_generate_from_more_than_enough_colors(self, fixtures: Fixtures) -> None:
        orig_colors = lib.make_colors("#7e118f #754fc7 #835d75 #807930 #9772ea")

        colors = list(Color.generate_from(orig_colors, 3))

        expected = lib.make_colors("#754fc7 #7e118f #9772ea")
        self.assertEqual(colors, expected)

    def test_generate_colors_when_2_input_colors_yields_gradient(
        self, fixtures: Fixtures
    ) -> None:
        orig_colors = lib.make_colors("#807930 #7e118f")

        colors = list(Color.generate_from(orig_colors, 7))

        # gradient goes from input colors ordered by luminocity
        expected = lib.make_colors(
            "#7e118f #7e1f80 #7e2e73 #7e3c65 #7f4c58 #7f5a4a #807930"
        )
        self.assertEqual(colors, expected)

    def test_generate_from_when_needs_more_colors_than_input(
        self, fixtures: Fixtures
    ) -> None:
        orig_colors = lib.make_colors("#7e118f #754fc7 #835d75 #7f564f")

        colors = list(Color.generate_from(orig_colors, 7))

        expected = lib.make_colors(
            "#754fc7 #835d75 #7e118f #7f564f #823cfd #e6f1c2 #6b30f9"
        )
        self.assertEqual(colors, expected)

    def test_randhue(self, fixtures: Fixtures) -> None:
        s, v = 59.0, 86.0

        c = Color.randhue(s, v)

        h, s, v = c.to_hsv()
        self.assertEqual(round(h), 68)
        self.assertEqual(round(s), 59)
        self.assertEqual(round(v), 86)

    def test_to_hsv(self, fixtures: Fixtures) -> None:
        h, s, v = Color("#9a59db").to_hsv()

        self.assertEqual(round(h), 270)
        self.assertEqual(round(s), 59)
        self.assertEqual(round(v), 86)

    def test_to_hsv_black(self, fixtures: Fixtures) -> None:
        h, s, v = Color("#000000").to_hsv()

        self.assertEqual(round(h), 359)
        self.assertEqual(round(s), 0)
        self.assertEqual(round(v), 0)

    def test_from_hsv(self, fixtures: Fixtures) -> None:
        hsv = (270, 59, 86)

        self.assertEqual(Color.from_hsv(hsv), Color("#9a59db"))

    def test_hsv_h_negative(self, fixtures: Fixtures) -> None:
        hsv = (-90, 59, 86)

        self.assertEqual(Color.from_hsv(hsv), Color("#9a59db"))

    def test_from_hsv_with_360(self, fixtures: Fixtures) -> None:
        hsv = (360, 59, 86)

        self.assertEqual(Color.from_hsv(hsv), Color("#db5959"))

    def test_hsv_gray(self, fixtures: Fixtures) -> None:
        hsv = (270, 0, 86)

        self.assertEqual(Color.from_hsv(hsv), Color("#dbdbdb"))

    def test_soften(self, fixtures: Fixtures) -> None:
        self.assertEqual(Color("#9a59db").soften(), Color("#c9a6ec"))

    def test_soften_with_softness(self, fixtures: Fixtures) -> None:
        self.assertEqual(Color("#9a59db").soften(softness=0.7), Color("#dec8f4"))


@given(lib.nprandom)
class DominantTests(TestCase):
    def test_dominant(self, fixtures: Fixtures) -> None:
        colors = lib.make_colors(
            "#FF5733 #33FF57 #3357FF #FFFF33 #FF33FF #33FFFF #FF8C00 #8A2BE2 #FFD700"
        )

        dominant_colors = Color.dominant(colors, 4)

        expected = ["#ffae19", "#5080f5", "#33ff57", "#ff33ff"]
        self.assertEqual([Color(i) for i in expected], dominant_colors)

        dominant_colors = Color.dominant(colors, 3)
        expected = ["#ffae19", "#7b6df7", "#33ff57"]
        self.assertEqual([Color(i) for i in expected], dominant_colors)


class ReplaceString(TestCase):
    def test1(self):
        colormap = {
            Color("#4a4a4a"): Color("#ffffff"),
            Color("#3a7e94"): Color("#000000"),
        }
        result = color.replace_string(lib.CSS, colormap)
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
        colormap = {Color("#333"): Color("#ffffff")}
        result = color.replace_string(lib.CSS, colormap)
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
        result = color.replace_string(lib.CSS, colormap)
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

    def test_init_with_invalid_values(self):
        good_values = {"red": 0.6, "green": 0.1, "blue": 0.9, "alpha": 1.0}

        for channel in ["red", "green", "blue", "alpha"]:
            bad_values = {**good_values, channel: 4.0}
            with self.assertRaises(ValueError) as ctx:
                ColorFloat(**bad_values)
            exc = ctx.exception
            self.assertEqual(exc.args, (f"{channel} must be between 0 and 1",))

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


class UngrayTests(TestCase):
    def test_ungrays(self):
        orig_colors = lib.make_colors("#acacac #660099 #555555 #bfbfbf #990066 #444444")

        colors = color.ungray(orig_colors)

        expected = lib.make_colors("#ac78ac #660099 #553b55 #bf86bf #990066 #443044")

        self.assertEqual(colors, expected)

    def test_can_specify_channel(self):
        orig_colors = lib.make_colors("#acacac #660099 #555555 #bfbfbf #990066 #444444")

        colors = color.ungray(orig_colors, channel="red")

        expected = lib.make_colors("#78acac #660099 #3b5555 #86bfbf #990066 #304444")

        self.assertEqual(colors, expected)

    def test_can_specify_amount(self):
        orig_colors = lib.make_colors("#acacac #660099 #555555 #bfbfbf #990066 #444444")

        colors = color.ungray(orig_colors, amount=1.3)

        expected = lib.make_colors("#ace0ac #660099 #556e55 #bff8bf #990066 #445844")

        self.assertEqual(colors, expected)

    def test_multiple_channels(self):
        orig_colors = lib.make_colors("#acacac #660099 #555555 #bfbfbf #990066 #444444")

        colors = color.ungray(orig_colors, channel=["red", "green"], amount=0)

        expected = lib.make_colors("#0000ac #660099 #000055 #0000bf #990066 #000044")

        self.assertEqual(colors, expected)

    def test_skips_black_and_white(self):
        orig_colors = lib.make_colors("#acacac #000000 #555555 #bfbfbf #990066 #ffffff")

        colors = color.ungray(orig_colors)

        expected = lib.make_colors("#ac78ac #000000 #553b55 #bf86bf #990066 #ffffff")

        self.assertEqual(colors, expected)


class RGBWTests(TestCase):
    def test_to_rgbw(self) -> None:
        c = Color(180, 48, 229)

        self.assertEqual((132, 0, 181, 48), c.to_rgbw())

    def test_from_rgwb(self) -> None:
        rgbw = (132, 0, 181, 48)

        self.assertEqual(Color(180, 48, 229), Color.from_rgbw(rgbw))


class IntensifyTests(TestCase):
    def test(self) -> None:
        c = Color("#bf86bf")

        self.assertEqual(Color("#bf5fbf"), c.intensify(0.7))

    def test_zero(self) -> None:
        c = Color("#bf86bf")

        self.assertEqual(c, c.intensify(0))


class ClosestTests(TestCase):
    colors = lib.make_colors(
        "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
    )

    def test(self) -> None:
        self.assert_closest("#bf86bf", "#9772ea")
        self.assert_closest("#0000ff", "#754fc7")
        self.assert_closest("#ffff00", "#9f934b")
        self.assert_closest("#008080", "#835d75")

    def test_is_closest_to_self(self) -> None:
        self.assert_closest("#35dfe9", "#35dfe9")

    def assert_closest(self, c1: str, c2: str) -> None:
        self.assertEqual(str(self.closest(c1)), c2)

    def closest(self, c: str) -> Color:
        return Color(c).closest(self.colors)


class ToArrayTests(TestCase):
    def test(self) -> None:
        c = Color("#7e118f")

        array = c.to_array()

        self.assertTrue(np.array_equal(array, np.array([126, 17, 143])), array)


class FromArrayTests(TestCase):
    def test(self) -> None:
        array = np.array([126, 17, 143])

        c = Color.from_array(array)

        self.assertEqual(c, Color("#7e118f"))
