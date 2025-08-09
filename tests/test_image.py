"""tests for larry.image"""

from unittest import TestCase, mock

from larry.color import Color
from larry.image import RasterImage, SVGImage, make_image_from_bytes

from . import lib, make_colors


# pylint: disable=missing-docstring
class MakeImageFromBytesTest(TestCase):
    def test_svg(self):
        image = make_image_from_bytes(lib.SVG_IMAGE)

        self.assertTrue(isinstance(image, SVGImage))

    def test_raster(self):
        image = make_image_from_bytes(lib.RASTER_IMAGE)

        self.assertTrue(isinstance(image, RasterImage))

    def test_not_an_image(self):
        with self.assertRaises(ValueError):
            make_image_from_bytes(b"\x01\x02\xff\xff")


class SVGImageTests(TestCase):
    image = SVGImage(lib.SVG_IMAGE)

    def test_colors(self):
        colors = sorted(self.image.colors, key=Color.luminocity)

        expected = make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff")

        self.assertEqual(colors, expected)

    def test_replace(self):
        orig_colors = make_colors("#000000 #254351 #7c8e96")
        new_colors = make_colors("#0000ff #00ff00 #ff0000")

        image = self.image.replace(orig_colors, new_colors)

        colors = sorted(image.colors, key=Color.luminocity)
        expected = make_colors("#0000ff #1c343f #ff0000 #666666 #00ff00 #ffffff")
        self.assertEqual(colors, expected)

    def test_bytes(self):
        self.assertEqual(bytes(self.image), lib.SVG_IMAGE)

    def test_str(self):
        self.assertEqual(str(self.image), lib.SVG_IMAGE.decode("UTF-8"))


class RasterImageTests(TestCase):
    image = RasterImage(lib.RASTER_IMAGE)

    def test_colors(self):
        colors = sorted(self.image.colors, key=Color.luminocity)

        expected = make_colors(
            # pylint: disable=line-too-long
            "#a889e9 #ae8ed9 #b594c9 #bc99ba #c39faa #c9a49a #d0aa8b #d7af7b #deb56b #e5bb5c"
        )
        self.assertEqual(colors, expected)

    def test_replace(self):
        orig_colors = make_colors("#a889e9 #b594c9 #c39faa #d0aa8b #deb56b")
        new_colors = make_colors("#0000ff #00ff00 #ff0000 #000000 #ffffff")

        image = self.image.replace(orig_colors, new_colors)

        colors = sorted(image.colors, key=Color.luminocity)
        expected = make_colors(
            "#000 #00f #f00 #0f0 #ae8ed9 #bc99ba #c9a49a #d7af7b #e5bb5c #fff"
        )
        self.assertEqual(colors, expected)

    def test_bytes(self) -> None:
        self.assertEqual(bytes(self.image), lib.RASTER_IMAGE)

    def test_bytes_oserror(self):
        image = self.image

        with mock.patch.object(image, "image") as mock_image:
            mock_image.save.side_effect = OSError("oops")
            bytes(image)

        mock_image.convert.assert_called_once_with("RGB")
        converted_image = mock_image.convert.return_value
        converted_image.save.assert_called_once_with(mock.ANY, image.image_format)
