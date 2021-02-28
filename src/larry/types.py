"""Larry data types"""
import io
import re
from abc import ABCMeta, abstractmethod
from typing import Iterable, Set

from PIL import Image

from larry.color import Color

COLOR_RE = re.compile(
    r"""
    (
        \#[0-9a-f]{6}|          # rrggbb
        \#[0-9a-f]{3}|          # rgb
        rgb\(\d+, *\d+, *\d+\)  # rgb(d, d, d)
    )
""",
    flags=re.X | re.I,
)


class ImageType(metaclass=ABCMeta):
    """A type of image instantiated from a byte stream"""

    @abstractmethod
    def __init__(self, data: bytes):
        pass

    @abstractmethod
    def __bytes__(self) -> bytes:
        pass

    @abstractmethod
    def get_colors(self) -> Iterable[Color]:
        """Return the Colors of this ImageType"""

    @abstractmethod
    def replace(self, orig_colors: Iterable[Color], new_colors: Iterable[Color]):
        """Mutate the ImageType by replacing orig_colors with new_colors"""


class SVGImage(ImageType):
    """An SVG image"""

    def __init__(self, data: bytes):
        super().__init__(data)
        self.svg = data.decode()

    def __bytes__(self):
        return self.svg.encode()

    def __str__(self):
        return self.svg

    def get_colors(self) -> Set[Color]:
        color_strings = COLOR_RE.findall(self.svg)

        return {Color(i) for i in color_strings}

    def replace(self, orig_colors: Iterable[Color], new_colors: Iterable[Color]):
        """Mutate the image by replacing orig_colors with new_colors"""
        for orig, new in zip(orig_colors, new_colors):
            color_str = str(new)
            self.svg = self.svg.replace(orig.colorspec, color_str)


class RasterImage(ImageType):
    """ImageType for Raster files"""

    def __init__(self, data: bytes):
        super().__init__(data)

        bytes_io = io.BytesIO(data)
        self.image = Image.open(bytes_io)

    def get_colors(self) -> Set[Color]:
        width, height = self.image.size
        color_map = {}

        for x in range(width):
            for y in range(height):
                pixel = self.image.getpixel((x, y))
                pixel_color = Color(pixel[:3])

                color_map[str(pixel_color)] = pixel_color

        colors = set(color_map.values())
        return colors

    def replace(self, orig_colors: Iterable[Color], new_colors: Iterable[Color]):
        """Mutate the Image by replacing orig_colors with new_colors"""
        color_map = {str(k): v for k, v in zip(orig_colors, new_colors)}
        width, height = self.image.size

        for x in range(width):
            for y in range(height):
                pixel = self.image.getpixel((x, y))
                pixel_color = Color(pixel[:3])

                if new := color_map.get(str(pixel_color), None):
                    self.image.putpixel((x, y), (new.red, new.green, new.blue))

    def __bytes__(self):
        bytes_io = io.BytesIO()
        self.image.save(bytes_io, self.image.format)

        return bytes_io.getvalue()
