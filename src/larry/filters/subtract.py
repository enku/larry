"""subtract color filter"""

import random
from configparser import ConfigParser

from larry.color import ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, _num_colors: int, _config: ConfigParser
) -> ColorGenerator:
    """XXX"""
    colors = list(orig_colors)
    color = random.choice(colors)
    sign = random.choice([-1, 1])

    if sign == -1:
        return (i - color for i in colors)

    return (i + color for i in colors)
