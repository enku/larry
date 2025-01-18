"""inverse color filter"""

from configparser import ConfigParser

from larry.color import ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, _num_colors: int, _config: ConfigParser
) -> ColorGenerator:
    """Return orig_colors inversed"""
    for color in orig_colors:
        yield color.inverse()
