# pylint: disable=missing-docstring
import random
from configparser import ConfigParser
from copy import deepcopy
from unittest import mock

from larry import filters
from larry.config import DEFAULT_INPUT_PATH

from . import TestCase, make_colors


class NewImageColorsTests(TestCase):
    config = ConfigParser()
    config.add_section("filters:test")
    config["filters:test"]["image"] = DEFAULT_INPUT_PATH

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
