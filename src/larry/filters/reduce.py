"""reduce color filter"""

import random
from configparser import ConfigParser

from larry.color import Color, ColorGenerator, ColorList

from .utils import closest_color


def cfilter(
    orig_colors: ColorGenerator, num_colors: int, config: ConfigParser
) -> ColorGenerator:
    """Reduce the number of distinct colors"""
    default_amount = 64
    amount = config.getint("filters:reduce", "amount", fallback=default_amount)

    if amount == 0 or num_colors <= amount:
        yield from orig_colors
        return

    colors = list(orig_colors)
    selected_colors: ColorList = random.choices(colors, k=amount)

    yield from (
        color if color in selected_colors else closest_color(color, selected_colors)
        for color in colors
    )
