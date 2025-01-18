"""luminocity color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, _num_colors: int, _config: ConfigParser
) -> ColorGenerator:
    """Return colors with the same luminocity as the original"""
    for color in orig_colors:
        yield Color.randcolor(lum=color.luminocity())
