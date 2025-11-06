# pylint: disable=missing-docstring
import importlib.metadata
import random
from inspect import signature
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given, params

from larry import filters
from larry.color import Color
from larry.config import DEFAULT_INPUT_PATH
from larry.filters.random import cfilter as random_filter

from . import lib

ORIG_COLORS = lib.make_colors(
    "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
)

FILTER_LIST = [ep.name for ep in importlib.metadata.entry_points(group="larry.filters")]


FilterTestCase = lib.FilterTestCase


@given(lib.tmpdir)
class ListFiltersTestsi(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        config_path = f"{fixtures.tmpdir}/larry.cfg"
        with open(config_path, "w", encoding="UTF-8") as fp:
            fp.write(
                """\
[larry]
filter = random | grayscale
"""
            )
        result = filters.list_filters(config_path)

        self.assertIn("[X] grayscale", result)
        self.assertIn("[X] random", result)
        self.assertIn("[ ] none", result)


class LoadFilterTests(TestCase):
    def test(self):

        func = filters.load_filter("random")

        self.assertIs(func, random_filter)

    def test_when_filter_does_not_exist(self):
        with self.assertRaises(filters.FilterNotFound):
            filters.load_filter("bogus")

    def test_when_filter_wont_load(self):
        with (
            self.assertRaises(filters.FilterNotFound),
            mock.patch.object(
                importlib.metadata.EntryPoint, "load", side_effect=ModuleNotFoundError
            ),
        ):
            filters.load_filter("random")


class FiltersListTests(TestCase):
    def test(self):
        filters_list = filters.filters_list()

        for name, func in filters_list:
            self.assertIsInstance(name, str)
            self.assert_is_filter_func(func)

    def assert_is_filter_func(self, func):
        sig = signature(func)
        parameters = sig.parameters
        self.assertEqual(len(parameters), 2)


class LuminocityTests(FilterTestCase):
    entry_point = "luminocity"

    @mock.patch("larry.color.random", random.Random(1))
    def test(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = lib.make_colors(
            "#51269a #20887c #82683a #22b00a #91a101 #c97867 #49e315 #adcc3f"
        )
        self.assertEqual(colors, expected)


class InverseTests(FilterTestCase):
    entry_point = "inverse"

    def test(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = lib.make_colors(
            "#81ee70 #8ab038 #7ca28a #7f86cf #688d15 #606cb4 #c617dd #ca2016"
        )
        self.assertEqual(colors, expected)


class GradientTests(FilterTestCase):
    entry_point = "gradient"

    @mock.patch("larry.color.random", random.Random(1))
    def test(self):
        config = lib.make_config("gradient")
        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#51269a #4d3da0 #4a55a7 #466cad #4384b4 #409cba #3cb3c1 #36e3ce"
        )
        self.assertEqual(colors, expected)

    @mock.patch("larry.color.random", random.Random(1))
    @mock.patch("larry.utils.random", random.Random(12345))
    def test_with_fuzz(self):
        config = lib.make_config("gradient", fuzz=60)
        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#8b41ff #7e4cf1 #7158e3 #6564d5 #5870c7 #4b7bb9 #3f87ab #269f90"
        )
        self.assertEqual(colors, expected)

    @mock.patch("larry.color.random", random.Random(1))
    def test_with_1_input_color(self) -> None:
        config = lib.make_config("gradient")
        orig_colors = [ORIG_COLORS[0]]
        colors = self.filter(orig_colors, config)

        expected = lib.make_colors("#51269a #14544c")

        self.assertEqual(expected, colors)


class ZipgradientTests(FilterTestCase):
    entry_point = "zipgradient"

    @mock.patch("larry.color.random", random.Random(1))
    def test(self):
        config = lib.make_config("zipgradient")
        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#47499c #3e6d9f #2bb5a4 #54b292 #7eaf80 #d2a95d #aabe49 #82d436"
        )
        self.assertEqual(colors, expected)

    @mock.patch("larry.color.random", random.Random(1))
    def test_with_colors_option(self):
        config = lib.make_config("zipgradient", colors=1)
        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#4d3da0 #4a55a7 #466cad #4384b4 #409cba #3cb3c1 #36e3ce #49dbbf"
        )
        self.assertEqual(colors, expected)

    def test_when_not_enough_steps(self):
        config = lib.make_config("zipgradient", colors=9)
        colors = self.filter(ORIG_COLORS, config)

        self.assertEqual(colors, ORIG_COLORS)


class ShuffleTests(FilterTestCase):
    entry_point = "shuffle"

    @mock.patch("larry.filters.shuffle.random", random.Random(1))
    def test(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = lib.make_colors(
            "#108f7e #c7754f #83755c #803078 #72ea97 #4b9f92 #3822e8 #df34e9"
        )
        self.assertEqual(colors, expected)


@mock.patch("larry.utils.random", random.Random(1))
class ShiftTests(FilterTestCase):
    entry_point = "shift"

    def test(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = lib.make_colors(
            "#754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9 #7e118f"
        )
        self.assertEqual(colors, expected)

    def test_shift_single_item(self):
        orig_colors = [ORIG_COLORS[0]]
        self.assertEqual(self.filter(orig_colors, None), orig_colors)


class PastelizeTests(FilterTestCase):
    entry_point = "pastelize"

    def test(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = lib.make_colors(
            "#ed7fff #a77fff #ff7fd0 #fff37f #a67fff #ffec7f #8eff7f #7ff7ff"
        )
        self.assertEqual(colors, expected)


class SoftenTests(FilterTestCase):
    entry_point = "soften"

    def test(self):
        config = lib.make_config("soften")
        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#bb6fc6 #b49ee3 #c1a5b6 #bfba83 #c9b5f4 #cfc798 #97f38b #95eef4"
        )
        self.assertEqual(colors, expected)

    def test_with_softness(self):
        config = lib.make_config("soften", softness="0.7")
        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#d5a2dd #d0c3ee #d9c6d2 #d8d5b0 #ded2f8 #e2ddbe #bff8b8 #bef5f8"
        )
        self.assertEqual(colors, expected)


class BrightenTests(FilterTestCase):
    entry_point = "brighten"

    def test(self):
        config = lib.make_config("brighten")

        colors = self.filter(ORIG_COLORS, config)

        # Kind of strange that brighten darkens by default
        expected = "#650e72 #5e3f9f #694a5e #666126 #795bbb #7f763c #2eba1b #2ab2ba"
        self.assertEqual(colors, lib.make_colors(expected))

    def test_with_percent_option(self):
        config = lib.make_config("brighten", percent=40)

        colors = self.filter(ORIG_COLORS, config)

        expected = "#b018c8 #a46fff #b782a4 #b3a943 #d3a0ff #dfce69 #50ff30 #4affff"
        self.assertEqual(colors, lib.make_colors(expected))


class SubtractTests(FilterTestCase):
    entry_point = "subtract"

    @mock.patch("larry.filters.subtract.random", random.Random(1))
    def test(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = "#00001a #000052 #000000 #001c00 #141575 #1c3600 #008b00 #008274"
        self.assertEqual(colors, lib.make_colors(expected))

    @mock.patch("larry.filters.subtract.random", random.Random(12))
    def test2(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = "#b3f0ff #aaffff #b8ffff #b5ffff #ccffff #d4ffff #6effff #6affff"
        self.assertEqual(colors, lib.make_colors(expected))


@mock.patch("larry.filters.randbright.random", random.Random(1))
class RandbrightTests(FilterTestCase):
    entry_point = "randbright"

    def test(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = "#861298 #24183d #9f718e #433f19 #ffd1ff #ffec79 #57ff34 #3bfaff"
        self.assertEqual(colors, lib.make_colors(expected))


class ContrastTests(FilterTestCase):
    entry_point = "contrast"

    def test(self):
        colors = self.filter(ORIG_COLORS, None)

        expected = "#000000 #24183d #4e3746 #6a6528 #8c69d8 #b1a454 #45ff29 #44ffff"
        self.assertEqual(colors, lib.make_colors(expected))


@mock.patch("larry.color.random", random.Random(1))
class SwapTests(FilterTestCase):
    entry_point = "swap"

    def test(self):
        config = lib.make_config("swap")

        colors = self.filter(ORIG_COLORS, config)

        expected = "#666666 #000000 #254351 #1c343f #7c8e96 #9caab0 #bdc6ca #ffffff"
        self.assertEqual(colors, lib.make_colors(expected))

    def test_with_source_image(self):
        config = lib.make_config("swap", source=DEFAULT_INPUT_PATH)

        colors = self.filter(ORIG_COLORS, config)

        expected = "#666666 #1c343f #000000 #254351 #7c8e96 #9caab0 #bdc6ca #ffffff"
        self.assertEqual(colors, lib.make_colors(expected))


class NoneTests(FilterTestCase):
    entry_point = "none"

    def test(self):
        config = lib.make_config("whatever")

        self.assertEqual(self.filter(ORIG_COLORS, config), ORIG_COLORS)


class VGATests(FilterTestCase):
    entry_point = "vga"

    def test(self):
        config = lib.make_config("vga")
        colors = self.filter(ORIG_COLORS, config)

        expected = "#600080 #6040c0 #804060 #806020 #8060e0 #808040 #20e020 #20c0e0"
        self.assertEqual(colors, lib.make_colors(expected))

    def test_with_bits_option(self):
        config = lib.make_config("vga", bits=4)
        colors = self.filter(ORIG_COLORS, config)

        expected = "#400080 #4040c0 #804040 #804000 #8040c0 #808040 #00c000 #00c0c0"
        self.assertEqual(colors, lib.make_colors(expected))


class GrayscaleTests(FilterTestCase):
    entry_point = "grayscale"

    def test(self):
        config = lib.make_config("grayscale")
        colors = self.filter(ORIG_COLORS, config)

        expected = "#8f8f8f #c7c7c7 #838383 #808080 #eaeaea #9f9f9f #e8e8e8 #e9e9e9"
        self.assertEqual(colors, lib.make_colors(expected))

    def test_with_saturation_setting(self):
        config = lib.make_config("grayscale", saturation=30)
        colors = self.filter(ORIG_COLORS, config)

        expected = "#89648f #9e8bc7 #835b74 #807c59 #b9a3ea #9f986f #aae8a2 #a3e5e9"
        self.assertEqual(colors, lib.make_colors(expected))

    def test_with_saturation_setting_above_100(self):
        config = lib.make_config("grayscale", saturation=130)
        colors = self.filter(ORIG_COLORS, config)

        expected = "#75008f #1600c7 #830044 #807100 #1700ea #9f8100 #00e800 #00d8e9"
        self.assertEqual(colors, lib.make_colors(expected))


@mock.patch("larry.filters.reduce.random", random.Random(1))
class ReduceTests(FilterTestCase):
    entry_point = "reduce"
    orig_colors = sorted(
        lib.make_colors(
            " #effeff #859673 #d8697f #abefdb #173347 #72de89 #69fc45 #fc8675 #f57074"
            " #7e1831 #50ed07 #77b098 #b8c839 #deb94d #8db935 #4ef582 #29fb4f #625c1d"
            " #39dea8 #0916da #250182 #38bc5e #f9a423 #098d23 #dc5c14 #a85e09 #2b0308"
            " #aaffdc #4291b4 #ba47ea #748c08 #142356 #3cb96d #d0d0fa #6bba34 #274974"
            " #2a9d54 #e21888 #9c2295 #38adc6"
        ),
        key=Color.luminocity,
    )

    def test_with_default_amount(self):
        config = lib.make_config("reduce")

        colors = self.filter(self.orig_colors, config)

        self.assertEqual(colors, self.orig_colors)

    def test_with_custom_amount(self):
        config = lib.make_config("reduce", amount=3)

        colors = self.filter(self.orig_colors, config)

        expected = (
            " #7e1831 #7e1831 #7e1831 #7e1831 #7e1831 #7e1831 #7e1831 #7e1831 #7e1831"
            " #4ef582 #7e1831 #7e1831 #4ef582 #7e1831 #f9a423 #7e1831 #4ef582 #4ef582"
            " #4ef582 #4ef582 #f9a423 #4ef582 #4ef582 #f9a423 #4ef582 #f9a423 #4ef582"
            " #4ef582 #f9a423 #4ef582 #f9a423 #f9a423 #4ef582 #4ef582 #f9a423 #4ef582"
            " #4ef582 #4ef582 #4ef582 #4ef582"
        )
        self.assertEqual(colors, lib.make_colors(expected))
        self.assertEqual(len(set(colors)), 3)

    def test_cannot_reduce_to_zero(self):
        config = lib.make_config("reduce", amount=0)

        colors = self.filter(self.orig_colors, config)

        self.assertEqual(colors, self.orig_colors)


class SubGradientTests(FilterTestCase):
    entry_point = "subgradient"
    orig_colors = sorted(
        lib.make_colors(
            "#ffa97f #231815 #7fd9ff #00ffbf #dd8138 #00b6ff #727f88 #7fccff"
        ),
        key=Color.luminocity,
    )

    def test(self):
        config = lib.make_config("subgradient")
        colors = self.filter(self.orig_colors, config)

        expected = "#231815 #727f88 #00b6ff #dd8138 #00ffbf #7fccff #ffa97f #7fd9ff"
        self.assertEqual(colors, lib.make_colors(expected))

    def test_with_size_argument(self):
        config = lib.make_config("subgradient", size=3)

        colors = self.filter(self.orig_colors, config)

        expected = (
            "#231815 #174c63 #00b6ff #dd8138 #bd9a7a #7fccff #ffa97f #d4b9a9 #7fd9ff"
        )
        self.assertEqual(colors, lib.make_colors(expected))

    def test_with_invalid_size(self):
        config = lib.make_config("subgradient", size=1)

        colors = self.filter(self.orig_colors, config)

        self.assertEqual(colors, self.orig_colors)

    def test_with_no_config(self):
        config = lib.make_config("bogus")

        colors = self.filter(self.orig_colors, config)

        self.assertEqual(colors, self.orig_colors)


class ColorifyTests(FilterTestCase):
    entry_point = "colorify"

    def test(self):
        orig_colors = lib.make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = lib.make_config("colorify", pastelize="0")
        new_colors = self.filter(orig_colors, config)

        # red is the default color
        self.assertEqual(new_colors, lib.make_colors("#dd0000 #ff7f7f #ff0000 #ffc0c0"))

    def test_custom_color_and_pastels(self):
        orig_colors = lib.make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = lib.make_config("colorify", pastelize="yes", color="#0000ff")

        new_colors = self.filter(orig_colors, config)

        self.assertEqual(new_colors, lib.make_colors("#0000dd #7f7fff #0000ff #c0c0ff"))


@mock.patch("larry.filters.dissolve.random", random.Random(1))
class DissolveTests(FilterTestCase):
    entry_point = "dissolve"

    def test(self):
        orig_colors = lib.make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = lib.make_config(
            "dissolve", image=DEFAULT_INPUT_PATH, amount=70, opacity=0.7
        )
        new_colors = self.filter(orig_colors, config)

        self.assertEqual(new_colors, lib.make_colors("#00dd00 #606752 #b2b2ff #ffc0ca"))

    def test_invalid_amount(self):
        orig_colors = lib.make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = lib.make_config(
            "dissolve", image=DEFAULT_INPUT_PATH, amount=700, opacity=0.7
        )
        with self.assertRaises(filters.FilterError):
            self.filter(orig_colors, config)


class DarkenTests(FilterTestCase):
    entry_point = "darken"

    def test(self):
        orig_colors = lib.make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = lib.make_config("darken", image=DEFAULT_INPUT_PATH, opacity=0.7)

        new_colors = self.filter(orig_colors, config)

        self.assertEqual(new_colors, lib.make_colors("#004200 #606752 #0000ff #938184"))


class LightenTests(FilterTestCase):
    entry_point = "lighten"

    def test(self):
        orig_colors = lib.make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = lib.make_config("lighten", image=DEFAULT_INPUT_PATH, opacity=0.7)

        new_colors = self.filter(orig_colors, config)

        self.assertEqual(new_colors, lib.make_colors("#00dd00 #ffde7f #b2b2ff #ffc0ca"))


class ChromeFocusTests(FilterTestCase):
    entry_point = "chromefocus"

    def test(self):
        config = lib.make_config("larry")

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#8f8f8f #754fc7 #838383 #808080 #9772ea #9f9f9f #e8e8e8 #e9e9e9"
        )
        self.assertEqual(colors, expected)

    def test_with_0_range(self):
        config = lib.make_config("chromefocus", range="0")

        colors = self.filter(ORIG_COLORS, config)

        self.assertEqual(colors, ORIG_COLORS)


class VibranceTests(FilterTestCase):
    entry_point = "vibrance"

    def test(self):
        config = lib.make_config("larry")

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#7e118f #754fc7 #835572 #807930 #946dea #9f9249 #39e822 #35dfe9"
        )
        self.assertEqual(colors, expected)


class ColorBalanceTests(FilterTestCase):
    entry_point = "colorbalance"

    def test(self):
        config = lib.make_config("larry")

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#78488b #7467a7 #7b6e7e #797c5b #8579b8 #898969 #56b454 #54afb8"
        )
        self.assertEqual(colors, expected)


class NeonizeTests(FilterTestCase):
    entry_point = "neonize"

    def test(self):
        config = lib.make_config("larry")

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#dc00ff #5000ff #ff00a1 #ffe800 #4e00ff #ffda00 #1dff00 #00f0ff"
        )
        self.assertEqual(colors, expected)


class KaleidoscopeTests(FilterTestCase):
    entry_point = "kaleidoscope"

    def test(self):
        config = lib.make_config("larry")
        colors = lib.make_colors(
            "#dc00ff #5000ff #ff00a1 #ffe800 #4e00ff #ffda00 #1dff00 #00f0ff"
        )
        expected = lib.make_colors(
            "#dc00ff #00f0ff #4e00ff #ffe800 #ffe800 #4e00ff #00f0ff #dc00ff"
        )

        filtered = self.filter(colors, config)

        self.assertEqual(len(filtered), len(colors))
        self.assertEqual(filtered, expected)

    def test_odd_number_length(self):
        config = lib.make_config("larry")
        colors = lib.make_colors(
            "#dc00ff #5000ff #ff00a1 #ffe800 #4e00ff #ffda00 #1dff00"
        )
        expected = lib.make_colors(
            "#dc00ff #1dff00 #4e00ff #ff00a1 #4e00ff #1dff00 #dc00ff"
        )

        filtered = self.filter(colors, config)

        self.assertEqual(len(filtered), len(colors))
        self.assertEqual(filtered, expected)


class IntensifyFilterTest(FilterTestCase):
    entry_point = "intensify"

    def test(self) -> None:
        config = lib.make_config("larry")

        colors = self.filter(ORIG_COLORS, config)

        expected = lib.make_colors(
            "#75008f #4c13c7 #834a6e #807508 #6e38ea #9f8d21 #00e800 #00dae9"
        )
        self.assertEqual(colors, expected)


class LuminizeFilterTest(FilterTestCase):
    entry_point = "luminize"

    def test(self) -> None:
        src = lib.make_colors("#a916e2 #ffc0cb #e2bd16")
        dst = lib.make_colors("#ff2cff #d7a2ab #deb916")
        config = lib.make_config("larry")

        colors = self.filter(src, config)

        self.assertEqual(colors, dst)


@params(filter_name=FILTER_LIST)
class AllFiltersTests(TestCase):
    def test_apply_filter(self, fixtures: Fixtures) -> None:
        cfilter = filters.load_filter(fixtures.filter_name)
        config = lib.make_config("larry")

        result = cfilter(ORIG_COLORS, config)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(ORIG_COLORS))

        for item in result:
            self.assertIsInstance(item, Color)
