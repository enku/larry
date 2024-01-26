# pylint: disable=missing-docstring
import random
from configparser import ConfigParser
from copy import deepcopy
from typing import Any
from unittest import mock

from larry import filters
from larry.color import Color
from larry.config import DEFAULT_INPUT_PATH

from . import TestCase, make_colors


def make_config(name: str, **settings: Any) -> ConfigParser:
    config = ConfigParser()
    section = f"filters:{name}"
    config.add_section(section)

    for key, value in settings.items():
        config[section][key] = str(value)

    return config


class ReduceTests(TestCase):
    orig_colors = sorted(
        make_colors(
            "#effeff #859673 #d8697f #abefdb #173347 #72de89 #69fc45 #fc8675 #f57074"
            " #7e1831 #50ed07 #77b098 #b8c839 #deb94d #8db935 #4ef582 #29fb4f #625c1d"
            " #39dea8 #0916da #250182 #38bc5e #f9a423 #098d23 #dc5c14 #a85e09 #2b0308"
            " #aaffdc #4291b4 #ba47ea #748c08 #142356 #3cb96d #d0d0fa #6bba34 #274974"
            " #2a9d54 #e21888 #9c2295 #38adc6"
        ),
        key=Color.luminocity,
    )

    def test(self):
        config = make_config("reduce")

        colors = filters.reduce(self.orig_colors, config)

        expected = "#e21888 #f9a423"
        self.assertEqual(colors, make_colors(expected))

    def test_with_custom_amount(self):
        config = make_config("reduce", amount=5)

        colors = filters.reduce(self.orig_colors, config)

        expected = "#173347 #2a9d54 #d8697f #fc8675 #d0d0fa"
        self.assertEqual(colors, make_colors(expected))


class SubGradientTests(TestCase):
    orig_colors = sorted(
        make_colors("#ffa97f #231815 #7fd9ff #00ffbf #dd8138 #00b6ff #727f88 #7fccff"),
        key=Color.luminocity,
    )

    def test(self):
        config = make_config("subgradient")
        colors = filters.subgradient(self.orig_colors, config)

        expected = "#231815 #727f88 #00b6ff #dd8138 #00ffbf #7fccff #ffa97f #7fd9ff"
        self.assertEqual(colors, make_colors(expected))

    def test_with_size_argument(self):
        config = make_config("subgradient", size=3)

        colors = filters.subgradient(self.orig_colors, config)

        expected = (
            "#231815 #11678a #00b6ff #dd8138 #aea69b #7fccff #ffa97f #bfc1bf #7fd9ff"
        )
        self.assertEqual(colors, make_colors(expected))

    def test_with_invalid_size(self):
        config = make_config("subgradient", size=1)

        colors = filters.subgradient(self.orig_colors, config)

        self.assertEqual(colors, self.orig_colors)

    def test_with_no_config(self):
        config = make_config("bogus")

        colors = filters.subgradient(self.orig_colors, config)

        self.assertEqual(colors, self.orig_colors)


class ColorifyTests(TestCase):
    def test(self):
        orig_colors = make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = make_config("colorify", pastelize="0")
        new_colors = filters.colorify(orig_colors, config)

        # red is the default color
        self.assertEqual(new_colors, make_colors("#dd0000 #ff7f7f #ff0000 #ffc0c0"))

    def test_custom_color_and_pastels(self):
        orig_colors = make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = make_config("colorify", pastelize="yes", color="#0000ff")

        new_colors = filters.colorify(orig_colors, config)

        self.assertEqual(new_colors, make_colors("#0000dd #7f7fff #0000ff #c0c0ff"))


@mock.patch("larry.filters.rand", random.Random(1))
class DissolveTests(TestCase):
    def test(self):
        orig_colors = make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = make_config(
            "dissolve", image=DEFAULT_INPUT_PATH, amount=70, opacity=0.7
        )
        new_colors = filters.dissolve(orig_colors, config)

        self.assertEqual(new_colors, make_colors("#00dd00 #606752 #b2b2ff #ffc0ca"))

    def test_invalid_amount(self):
        orig_colors = make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = make_config(
            "dissolve", image=DEFAULT_INPUT_PATH, amount=700, opacity=0.7
        )
        with self.assertRaises(filters.FilterError):
            filters.dissolve(orig_colors, config)


class DarkenTests(TestCase):
    def test(self):
        orig_colors = make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = make_config("darken", image=DEFAULT_INPUT_PATH, opacity=0.7)

        new_colors = filters.darken(orig_colors, config)

        self.assertEqual(new_colors, make_colors("#004200 #606752 #0000ff #938184"))


class LightenTests(TestCase):
    def test(self):
        orig_colors = make_colors("#00dd00 #ffde7f #0000ff #ffc0cb")
        config = make_config("lighten", image=DEFAULT_INPUT_PATH, opacity=0.7)

        new_colors = filters.lighten(orig_colors, config)

        self.assertEqual(new_colors, make_colors("#00dd00 #ffde7f #b2b2ff #ffc0ca"))


class GetOpacityTests(TestCase):
    config = make_config("test", opacity=0.5, foo=0.7, bar=7.0)

    def test(self):
        result = filters.get_opacity(self.config, "test")

        self.assertEqual(result, 0.5)

    def test_fallback(self):
        result = filters.get_opacity(self.config, "test", "bogus")

        self.assertEqual(result, 1.0)

    def test_custom_name(self):
        result = filters.get_opacity(self.config, "test", "foo")

        self.assertEqual(result, 0.7)

    def test_bad_value(self):
        with self.assertRaises(filters.FilterError):
            filters.get_opacity(self.config, "test", "bar")


class NewImageColorsTests(TestCase):
    config = make_config("test", image=DEFAULT_INPUT_PATH)

    def test(self):
        colors = filters.new_image_colors(6, self.config, "test")

        expected = make_colors("#000000 #1c343f #ffffff #666666 #254351 #7c8e96")
        self.assertEqual(colors, expected)

    @mock.patch("larry.filters.rand", random.Random(1))
    def test_with_shuffle(self):
        config = deepcopy(self.config)
        config["filters:test"]["shuffle"] = "1"

        colors = filters.new_image_colors(6, config, "test")

        expected = make_colors("#ffffff #666666 #7c8e96 #000000 #254351 #1c343f")
        self.assertEqual(colors, expected)

    def test_with_more_colors_than_source_image_cycle(self):
        colors = filters.new_image_colors(8, self.config, "test")

        expected = make_colors(
            "#000000 #1c343f #ffffff #666666 #254351 #7c8e96 #000000 #1c343f"
        )
        self.assertEqual(colors, expected)
