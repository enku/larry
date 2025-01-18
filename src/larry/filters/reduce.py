"""reduce color filter"""

from configparser import ConfigParser

from larry.color import ColorGenerator

from .utils import closest_color, get_dominant_colors


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Reduce the number of distinct colors"""
    colors = list(orig_colors)
    num_colors = len(colors)
    amount = num_colors // 20

    try:
        amount = config["filters:reduce"].getint("amount", fallback=amount)
    except KeyError:
        pass

    if amount == 0:
        yield from colors
        return

    dominant_colors = get_dominant_colors(colors, amount)

    for color in colors:
        if color in dominant_colors:
            yield color
        else:
            yield closest_color(color, dominant_colors)
