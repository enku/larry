"""contrast color filter"""

from configparser import ConfigParser

from larry import ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """The darks are so dark and the brights are so bright"""
    step = 255 / len(orig_colors)

    return [color.luminize(i * step) for i, color in enumerate(orig_colors)]
