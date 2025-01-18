"""pastelize color filter"""

from configparser import ConfigParser

from larry.color import ColorGenerator


def cfilter(orig_colors: ColorGenerator, _config: ConfigParser) -> ColorGenerator:
    """Pastelize all the original colors"""
    for color in orig_colors:
        yield color.pastelize()
