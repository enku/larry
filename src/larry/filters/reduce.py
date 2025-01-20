"""reduce color filter"""

import random
from configparser import ConfigParser

from larry import ColorList

from .utils import closest_color


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Reduce the number of distinct colors"""
    default_amount = 64
    amount = config.getint("filters:reduce", "amount", fallback=default_amount)

    num_colors = len(orig_colors)
    if amount == 0 or num_colors <= amount:
        return orig_colors

    colors = list(orig_colors)
    selected_colors: ColorList = random.choices(colors, k=amount)

    return [
        color if color in selected_colors else closest_color(color, selected_colors)
        for color in colors
    ]
