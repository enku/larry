"""inverse color filter"""

from configparser import ConfigParser

from larry import ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Return orig_colors inversed"""
    return [i.inverse() for i in orig_colors]
