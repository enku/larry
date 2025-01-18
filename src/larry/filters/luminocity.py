"""luminocity color filter"""

from configparser import ConfigParser

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Return colors with the same luminocity as the original"""
    return [Color.randcolor(lum=i.luminocity()) for i in orig_colors]
