"""Replace colors on the Larry the Cow wallpaper"""
import configparser
import logging
import os
import random
import re
from typing import Callable

import pkg_resources

from larry.types import Color

__version__ = "1.6.1"

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
ORIG_FILENAME = os.path.join(DATA_DIR, "gentoo-cow-gdm-remake.svg")
LOGGER = logging.getLogger("larry")
CONFIG_PATH = os.path.expanduser("~/.config/larry.cfg")
CONFIG = configparser.ConfigParser()
CONFIG["DEFAULT"]["input"] = ORIG_FILENAME
CONFIG["DEFAULT"]["fuzz"] = "10"
CONFIG.read(CONFIG_PATH)


class PluginNotFound(LookupError):
    """Unable to find the requested plugin"""


def randsign(num: int) -> int:
    return random.choice([-1, 1]) * random.randint(0, num)


def load_algo(name: str) -> Callable:
    """Load the algo with the given name"""
    iter_ = pkg_resources.iter_entry_points("larry.algos", name)

    try:
        return next(iter_).load()
    except (ModuleNotFoundError, StopIteration) as error:
        raise PluginNotFound(name) from error


def rrggbb(color: str, theme_color: Color, css: str) -> str:
    color = "#" + color
    orig_color = Color(color)
    new_color = orig_color.colorify(theme_color)

    return re.sub(str(color), str(new_color), css, flags=re.I)


def rgb(color: str, theme_color: Color, css: str) -> str:
    red, green, blue = [int(float(i)) for i in color.split(",")]
    orig_color = Color((red, green, blue))
    new_color = orig_color.colorify(theme_color)
    re_str = re.escape(f"rgb({color})")

    return re.sub(re_str, str(new_color), css, flags=re.I)


def rgba(color: str, theme_color: Color, css: str) -> str:
    parts = color.split(",")
    red, green, blue, *_ = [int(float(i)) for i in parts]
    orig_color = Color((red, green, blue))
    new_color = orig_color.colorify(theme_color)
    re_str = re.escape("rgba({},{},{},".format(*parts[:3]))
    re_str = re_str + r"(" + re.escape(parts[-1]) + r")\)"
    new_str = "rgba({},{},{},\\1)".format(
        new_color.red, new_color.green, new_color.blue
    )

    return re.sub(re_str, new_str, css, flags=re.I)


if "larry" not in CONFIG:
    CONFIG["larry"] = {}
