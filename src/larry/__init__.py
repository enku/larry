"""Replace colors on the Larry the Cow wallpaper"""
from __future__ import annotations

import configparser
import logging
import os
import random
import re
from abc import ABCMeta, abstractmethod
from io import BytesIO
from typing import Callable, Iterable, List, Set

import pkg_resources
from PIL import Image as PillowImage

from larry.color import Color, ColorGenerator, ColorList

__version__ = pkg_resources.get_distribution("larry").version

BASE_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.expanduser("~/.config/larry.cfg")
DATA_DIR = os.path.join(BASE_DIR, "data")
ORIG_FILENAME = os.path.join(DATA_DIR, "gentoo-cow-gdm-remake.svg")
LOGGER = logging.getLogger("larry")


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

ConfigType = configparser.SectionProxy


class Image(metaclass=ABCMeta):
    """A type of image instantiated from a byte stream"""

    implementations: List[Image] = []

    @classmethod
    def __init_subclass__(cls):
        Image.implementations.insert(0, cls)

    @abstractmethod
    def __init__(self, data: bytes):
        pass

    @abstractmethod
    def __bytes__(self) -> bytes:
        """Convert to a byte stream"""

    @abstractmethod
    def get_colors(self) -> Iterable[Color]:
        """Return the Colors of this Image"""

    @abstractmethod
    def replace(self, orig_colors: Iterable[Color], new_colors: Iterable[Color]):
        """Mutate the Image by replacing orig_colors with new_colors"""

    @classmethod
    def from_bytes(cls, data: bytes) -> Image:
        """Return an instance of Image using data"""
        for implementation in cls.implementations:
            try:
                return implementation(data)
            except Exception as error:
                continue

        raise error


class SVGImage(Image):
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
            self.svg = self.svg.replace(str(orig.colorspec), color_str)


class RasterImage(Image):
    """Image for Raster files"""

    def __init__(self, data: bytes):
        super().__init__(data)

        bytes_io = BytesIO(data)
        self.image = PillowImage.open(bytes_io)

        # We want to deal with everything as an RGBA but but go back to the orignal
        # format/mode when converting to bytes
        self.image_format = self.image.format
        self.image_mode = self.image.mode
        self.image = self.image.convert("RGBA")

    def get_colors(self) -> Set[Color]:
        width, height = self.image.size

        pixels = {
            self.image.getpixel((x, y))[:3] for y in range(height) for x in range(width)
        }
        # for x in range(width):  # pylint: disable=invalid-name
        #    for y in range(height):  # pylint: disable=invalid-name
        #        pixels.add(self.image.getpixel((x, y))[:3])

        return {Color(i) for i in pixels}

    def replace(self, orig_colors: Iterable[Color], new_colors: Iterable[Color]):
        """Mutate the Image by replacing orig_colors with new_colors"""
        width, height = self.image.size

        # map original rgb tuples to new
        color_map = dict(
            (orig.rgb, new.rgb) for orig, new in zip(orig_colors, new_colors)
        )

        for x in range(width):  # pylint: disable=invalid-name
            for y in range(height):  # pylint: disable=invalid-name
                *rgb, alpha = self.image.getpixel((x, y))

                try:
                    new = color_map[(*rgb,)]
                except KeyError:
                    continue

                self.image.putpixel((x, y), (*new, alpha))

    def __bytes__(self):
        bytes_io = BytesIO()

        try:
            self.image.save(bytes_io, self.image_format)
        except OSError:
            self.image.convert("RGB").save(bytes_io, self.image_format)

        return bytes_io.getvalue()


def randsign(num: int) -> int:
    return random.choice([-1, 1]) * random.randint(0, num)


def load_config(path: str = CONFIG_PATH) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config["DEFAULT"]["input"] = ORIG_FILENAME
    config.read(path)

    return config
