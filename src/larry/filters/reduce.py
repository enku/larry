"""reduce color filter"""

from configparser import ConfigParser

from larry import ColorList

from .utils import closest_color, get_dominant_colors


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Reduce the number of distinct colors"""
    num_colors = len(orig_colors)
    amount = num_colors // 20

    try:
        amount = config["filters:reduce"].getint("amount", fallback=amount)
    except KeyError:
        pass

    if amount == 0:
        return orig_colors

    dominant_colors = get_dominant_colors(orig_colors, amount)
    colors = []

    for color in orig_colors:
        if color in dominant_colors:
            colors.append(color)
        else:
            colors.append(closest_color(color, dominant_colors))
    return colors
