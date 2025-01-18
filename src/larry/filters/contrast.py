"""contrast color filter"""

from configparser import ConfigParser

from larry.color import ColorGenerator


def cfilter(orig_colors: ColorGenerator, _config: ConfigParser) -> ColorGenerator:
    """The darks are so dark and the brights are so bright"""
    colors = list(orig_colors)
    num_colors = len(colors)
    step = 255 / num_colors

    lum = 0.0
    for color in colors:
        yield color.luminize(lum)
        lum += step
