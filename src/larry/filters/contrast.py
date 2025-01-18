"""contrast color filter"""

from configparser import ConfigParser

from larry.color import ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, num_colors: int, _config: ConfigParser
) -> ColorGenerator:
    """The darks are so dark and the brights are so bright"""
    step = 255 / num_colors

    lum = 0.0
    for color in orig_colors:
        yield color.luminize(lum)
        lum += step
