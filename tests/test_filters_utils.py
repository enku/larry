"""Tests for larry.filters.utils"""

# pylint: disable=missing-docstring

import random
from copy import deepcopy
from unittest import TestCase, mock

from larry import filters
from larry.config import DEFAULT_INPUT_PATH
from larry.filters import utils

from .lib import make_colors, make_config


class NewImageColorsTests(TestCase):
    config = make_config("test", image=DEFAULT_INPUT_PATH)

    def test(self):
        colors = utils.new_image_colors(6, self.config, "test")

        expected = make_colors("#000000 #1c343f #ffffff #666666 #254351 #7c8e96")
        self.assertEqual(colors, expected)

    @mock.patch("larry.filters.utils.random", random.Random(1))
    def test_with_shuffle(self):
        config = deepcopy(self.config)
        config["filters:test"]["shuffle"] = "1"

        colors = utils.new_image_colors(6, config, "test")

        expected = make_colors("#ffffff #666666 #7c8e96 #000000 #254351 #1c343f")
        self.assertEqual(colors, expected)

    def test_with_more_colors_than_source_image_cycle(self):
        colors = utils.new_image_colors(8, self.config, "test")

        expected = make_colors(
            "#000000 #1c343f #ffffff #666666 #254351 #7c8e96 #000000 #1c343f"
        )
        self.assertEqual(colors, expected)


class GetOpacityTests(TestCase):
    config = make_config("test", opacity=0.5, foo=0.7, bar=7.0)

    def test(self):
        result = utils.get_opacity(self.config, "test")

        self.assertEqual(result, 0.5)

    def test_fallback(self):
        result = utils.get_opacity(self.config, "test", "bogus")

        self.assertEqual(result, 1.0)

    def test_custom_name(self):
        result = utils.get_opacity(self.config, "test", "foo")

        self.assertEqual(result, 0.7)

    def test_bad_value(self):
        with self.assertRaises(filters.FilterError):
            utils.get_opacity(self.config, "test", "bar")
