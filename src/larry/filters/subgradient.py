"""subgradient color filter"""

from configparser import ConfigParser
from itertools import islice

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Like zipgradient, but gradients are a subset of the original colors"""
    num_colors = len(orig_colors)
    index = 0
    size = num_colors // 20
    new_colors: ColorList = []

    try:
        size = config["filters:subgradient"].getint("size", fallback=size)
    except KeyError:
        pass

    if size < 2:
        return orig_colors

    while chunk := orig_colors[index : index + size]:
        grad = Color.gradient(chunk[0], chunk[-1], size)
        new_colors.extend(grad)
        index += size

    return new_colors
