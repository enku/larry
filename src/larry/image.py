"""Facilities for manipulating images"""

from __future__ import annotations

from io import BytesIO
from typing import Iterable, Protocol, Type

import numpy as np
from PIL import Image as PillowImage

from larry.color import COLORS_RE, Color, replace_string

IMAGE_TYPES: list[Type[Image]] = []


class Image(Protocol):
    """A type of image instantiated from a byte stream"""

    def __init__(self, data: bytes) -> None:
        """Initializer"""

    def __bytes__(self) -> bytes:
        """Convert to a byte stream"""

    @property
    def colors(self) -> Iterable[Color]:
        """Return the Colors of this Image"""

    def replace(
        self, orig_colors: Iterable[Color], new_colors: Iterable[Color]
    ) -> Image:
        """Return a new image by orig_colors with new_colors"""


def register_image_type(cls: Type[Image]) -> Type[Image]:
    """Decorator to register the given image type"""
    IMAGE_TYPES.append(cls)
    return cls


@register_image_type
class SVGImage:
    """An SVG image"""

    def __init__(self, data: bytes):
        self.svg = data.decode()

    def __bytes__(self):
        return self.svg.encode()

    def __str__(self):
        return self.svg

    def color_strings(self) -> list[str]:
        """Return a list of all the colors strings in the SVGImage"""
        return COLORS_RE.findall(self.svg)

    @property
    def colors(self) -> set[Color]:
        """Return the Colors of this Image"""
        return {Color(i) for i in self.color_strings()}

    def replace(
        self, orig_colors: Iterable[Color], new_colors: Iterable[Color]
    ) -> SVGImage:
        """Return a new image by orig_colors with new_colors"""
        color_map = dict(zip(orig_colors, new_colors))
        svg = replace_string(self.svg, color_map)

        return type(self)(svg.encode())


@register_image_type
class RasterImage:
    """Image for Raster files"""

    def __init__(self, data: bytes):
        bytes_io = BytesIO(data)
        self.image = PillowImage.open(bytes_io)

        # We want to deal with everything as an RGBA but but go back to the original
        # format/mode when converting to bytes
        self.image_format = self.image.format
        self.image_mode = self.image.mode
        self.image = self.image.convert("RGBA")

    @property
    def colors(self) -> set[Color]:
        """Return the Colors of this Image"""
        array = np.array(self.image)[:, :, :3]

        return {
            Color.from_array(array[i, j])
            for i in range(array.shape[0])
            for j in range(array.shape[1])
        }

    def replace(
        self, orig_colors: Iterable[Color], new_colors: Iterable[Color]
    ) -> RasterImage:
        """Return a new image by orig_colors with new_colors"""
        width, height = self.image.size

        # map original rgb tuples to new
        color_map = dict((orig, new) for orig, new in zip(orig_colors, new_colors))

        new_image = type(self)(bytes(self))

        for x in range(width):  # pylint: disable=invalid-name
            for y in range(height):  # pylint: disable=invalid-name
                *rgb, alpha = self.image.getpixel((x, y))

                try:
                    new = color_map[Color(*rgb)]
                except KeyError:
                    continue

                new_image.image.putpixel((x, y), (*new, alpha))

        return new_image

    def __bytes__(self) -> bytes:
        bytes_io = BytesIO()

        try:
            self.image.save(bytes_io, self.image_format)
        except OSError:
            self.image.convert("RGB").save(bytes_io, self.image_format)

        return bytes_io.getvalue()


def make_image_from_bytes(data: bytes) -> Image:
    """Return an instance of Image using data"""
    for image_type in IMAGE_TYPES:
        try:
            return image_type(data)
        except Exception:  # pylint: disable=broad-except
            continue

    raise ValueError("Could not instantiate image type from data provided")
