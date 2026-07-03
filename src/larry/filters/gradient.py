"""gradient color filter"""

import random
from configparser import ConfigParser

from larry import Color, ColorList, utils


def cfilter(colors: ColorList, config: ConfigParser) -> ColorList:
    """Return gradient within the same luminocity range as the original"""
    num_colors = len(colors)

    # Make sure we have at least 2 colors
    if num_colors == 1:
        colors = colors * 2
        num_colors = 2

    fuzz = config.getint("filters:gradient", "fuzz", fallback=0)

    try:
        num_grad_colors = config.getint("filters:gradient", "num_colors", fallback=2)
    except ValueError:
        if config.get("filters:gradient", "num_colors") == "random":
            max_random = config.getint("filters:gradient", "max_random", fallback=7)
            num_grad_colors = random.randint(2, (min(num_colors, max_random)))
        else:
            raise

    indices = [
        round(i * (num_colors - 1) / (num_grad_colors - 1))
        for i in range(num_grad_colors)
    ]
    lums = [
        min(max(colors[i].luminocity(), 0), 255) + utils.randsign(fuzz) for i in indices
    ]

    return list(Color.gradient2([Color.randcolor(lum=lum) for lum in lums], num_colors))
