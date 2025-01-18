"""subgradient color filter"""

from configparser import ConfigParser
from itertools import islice

from larry.color import Color, ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, num_colors: int, config: ConfigParser
) -> ColorGenerator:
    """Like zipgradient, but gradients are a subset of the original colors"""
    size = num_colors // 20
    size = config.getint("filters:subgradient", "size", fallback=size)

    if size < 2:
        yield from orig_colors
        return

    while chunk := list(islice(orig_colors, size)):
        yield from Color.gradient(chunk[0], chunk[-1], size)
