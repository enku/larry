"""Change the luminocity of colors"""

from configparser import ConfigParser

from larry.color import ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Give all the colors the same luminocity"""
    luminance = config.getfloat("filters:luminize", "luminance", fallback=178.5)

    return [color.luminize(luminance) for color in orig_colors]
