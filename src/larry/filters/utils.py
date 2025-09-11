"""color filter utilities"""

import io
import random
from configparser import ConfigParser
from importlib.metadata import entry_points
from itertools import cycle

import numpy as np
from scipy.spatial import distance

from larry.color import Color, ColorList
from larry.config import load as load_config
from larry.filters.types import Filter, FilterError, FilterNotFound
from larry.image import make_image_from_bytes
from larry.io import read_file


def list_filters(config_path: str) -> str:
    """Return text displaying available filters and enabled status"""
    output = io.StringIO()
    config = load_config(config_path)
    enabled_filter = config["larry"].get("filter", "gradient").split()

    for name, func in filters_list():
        func_doc = func.__doc__ or ""
        doc = func_doc.split("\n", 1)[0].strip()
        enabled = "X" if name in enabled_filter else " "

        print(f"[{enabled}] {name:20} {doc}", file=output)

    return output.getvalue()


def load_filter(name: str) -> Filter:
    """Load the filter with the given name"""
    filters = entry_points().select(group="larry.filters", name=name)

    if not filters:
        raise FilterNotFound(name)

    try:
        return tuple(filters)[0].load()
    except ModuleNotFoundError as error:
        raise FilterNotFound(name) from error


def filters_list() -> list[tuple[str, Filter]]:
    """Return a list of tuple of (filter_name, filter_func) for all filters"""
    return [(i.name, i.load()) for i in entry_points().select(group="larry.filters")]


def get_opacity(config: ConfigParser, section: str, name: str = "opacity") -> float:
    """Return the opacity setting from the config & section

    If the opacity value is not valid, raise FilterError.
    """
    opacity = config.getfloat(f"filters:{section}", name, fallback=1.0)

    if not 0 <= opacity <= 1:
        raise FilterError(f"'opacity' must be in range [0..1]. Actual {opacity}")

    return opacity


def new_image_colors(
    orig_colors: ColorList,
    config: ConfigParser,
    section: str,
    name: str = "image",
    count: int | None = None,
) -> ColorList:
    """Return count colors from the image specified in config

    If the image has fewer colors than requested, the colors are cycled.

    The default count is the number of colors in the original list.

    If the no image file is given in the config, colors are selected from the original
    list.
    """
    if count is None:
        count = len(orig_colors)

    section = f"filters:{section}"
    image_colors = list(orig_colors)

    if filename := config.get(section, name, fallback=""):
        image_colors = list(make_image_from_bytes(read_file(filename)).colors)

    if config.getboolean(section, "shuffle", fallback=False):
        random.shuffle(image_colors)
    replacer_colors_cycle = cycle(image_colors)

    return [next(replacer_colors_cycle) for _ in range(count)]


def closest_color(color: Color, colors: ColorList) -> Color:
    """Given the list of Colors, return the one closest to the given color"""
    distances = [distance.euclidean(color, c) for c in colors]

    return colors[np.argmin(distances)]


def parse_range(range_str: str) -> tuple[float, float] | None:
    """Parse float range from the config string

    range_str should look like:

        "0.8 - 1.0"

    If the string is not parsable, None is returned.
    """
    start, dash, stop = range_str.partition("-")

    if not all([start, dash, stop]):
        return None

    return (float(start.strip()), float(stop.strip()))
