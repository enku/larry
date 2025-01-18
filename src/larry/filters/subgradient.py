"""subgradient color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorGenerator


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Like zipgradient, but gradients are a subset of the original colors"""
    colors = list(orig_colors)
    num_colors = len(colors)
    index = 0
    size = num_colors // 20

    try:
        size = config["filters:subgradient"].getint("size", fallback=size)
    except KeyError:
        pass

    if size < 2:
        yield from colors
        return

    while chunk := colors[index : index + size]:
        yield from Color.gradient(chunk[0], chunk[-1], size)
        index += size
