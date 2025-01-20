"""pastelize color filter"""

from configparser import ConfigParser

from larry import ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Pastelize all the original colors"""
    return [orig_color.pastelize() for orig_color in orig_colors]
