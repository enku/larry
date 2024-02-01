# pylint: disable=missing-docstring
import random
from unittest import mock

import larry
from larry import config
from larry.color import Color

from . import RASTER_IMAGE, SVG_IMAGE, TestCase, make_colors


class ConfigTypeTests(TestCase):
    def test(self):
        with self.assertWarns(DeprecationWarning):
            config_type = larry.ConfigType

        self.assertIs(config_type, config.ConfigType)


class MakeImageFromBytesTest(TestCase):
    def test_svg(self):
        image = larry.make_image_from_bytes(SVG_IMAGE)

        self.assertTrue(isinstance(image, larry.SVGImage))

    def test_raster(self):
        image = larry.make_image_from_bytes(RASTER_IMAGE)

        self.assertTrue(isinstance(image, larry.RasterImage))

    def test_not_an_image(self):
        with self.assertRaises(ValueError):
            larry.make_image_from_bytes(b"\x01\x02\xFF\xFF")


class SVGImageTests(TestCase):
    image = larry.SVGImage(SVG_IMAGE)

    def test_get_colors(self):
        colors = sorted(self.image.get_colors(), key=Color.luminocity)

        expected = make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff")

        self.assertEqual(colors, expected)

    def test_replace(self):
        orig_colors = make_colors("#000000 #254351 #7c8e96")
        new_colors = make_colors("#0000ff #00ff00 #ff0000")

        image = self.image.replace(orig_colors, new_colors)

        colors = sorted(image.get_colors(), key=Color.luminocity)
        expected = make_colors("#0000ff #1c343f #ff0000 #666666 #00ff00 #ffffff")
        self.assertEqual(colors, expected)

    def test_bytes(self):
        self.assertEqual(bytes(self.image), SVG_IMAGE)

    def test_str(self):
        self.assertEqual(str(self.image), SVG_IMAGE.decode("UTF-8"))


class RasterImageTests(TestCase):
    image = larry.RasterImage(RASTER_IMAGE)

    def test_get_colors(self):
        colors = sorted(self.image.get_colors(), key=Color.luminocity)

        expected = make_colors(
            "#a889e9 #ae8ed9 #b594c9 #bc99ba #c39faa #c9a49a #d0aa8b #d7af7b #deb56b #e5bb5c"
        )
        self.assertEqual(colors, expected)

    def test_replace(self):
        orig_colors = make_colors("#a889e9 #b594c9 #c39faa #d0aa8b #deb56b")
        new_colors = make_colors("#0000ff #00ff00 #ff0000 #000000 #ffffff")

        image = self.image.replace(orig_colors, new_colors)

        colors = sorted(image.get_colors(), key=Color.luminocity)
        expected = make_colors(
            "#000000 #0000ff #ff0000 #00ff00 #ae8ed9 #bc99ba #c9a49a #d7af7b #e5bb5c #ffffff"
        )
        self.assertEqual(colors, expected)

    def test_bytes(self):
        self.assertEqual(bytes(self.image), RASTER_IMAGE)
