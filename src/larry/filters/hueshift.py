"""hueshift color filter"""

import random
import sys
from configparser import ConfigParser

from larry.color import Color, ColorList

DEFAULT_AMOUNT = -90.0


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Shift the hues of each color by a given amount"""
    amount_str = config.get("filters:hueshift", "amount", fallback="")
    amount = get_amount(amount_str)

    return [
        Color.from_hsv((((h + amount) % 360), s, v))
        for color in orig_colors
        for h, s, v in [color.to_hsv()]
    ]


def get_amount(amount_str: str, default: float = DEFAULT_AMOUNT) -> float:
    """Return the given amount string as a float.

    If the string is the empty string, the default value is returned

    If the string == "random" then a random float [0, 360] is returned

    If the string cannot translated to a float, a message is printed to stderr and the
    default value is returned.
    """
    if amount_str == "":
        return default

    if amount_str == "random":
        return random.uniform(0, 360)

    try:
        return float(amount_str)
    except ValueError:
        print(f"amount could not be parsed as float: {amount_str}", file=sys.stderr)
        return default
