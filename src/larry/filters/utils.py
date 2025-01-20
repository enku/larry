"""color filter utilities"""

import random
from collections import Counter
from configparser import ConfigParser
from itertools import cycle

import numpy as np
from scipy.spatial import distance

from larry import Color, ColorList, make_image_from_bytes
from larry.io import read_file

from . import FilterError


def get_opacity(config: ConfigParser, section: str, name: str = "opacity") -> float:
    """Return the opacity setting from the config & section

    If the opacity value is not valid, raise FilterError.
    """
    opacity = config[f"filters:{section}"].getfloat(name, fallback=1.0)

    if not 0 <= opacity <= 1:
        raise FilterError(f"'opacity' must be in range [0..1]. Actual {opacity}")

    return opacity


def new_image_colors(
    count: int, config: ConfigParser, section: str, name: str = "image"
) -> ColorList:
    """Return count colors from the image specified in config

    If the image has fewer colors than requested, the colors are cycled.
    """
    image_colors = list(
        make_image_from_bytes(
            read_file(config[f"filters:{section}"].get(name))
        ).get_colors()
    )
    if config[f"filters:{section}"].getboolean("shuffle", fallback=False):
        random.shuffle(image_colors)
    replacer_colors_cycle = cycle(image_colors)

    return [next(replacer_colors_cycle) for _ in range(count)]


def closest_color(color: Color, colors: ColorList) -> Color:
    """Given the list of Colors, return the one closest to the given color"""
    distances = [distance.euclidean(color, c) for c in colors]

    return colors[np.argmin(distances)]
